// Read-only proof of program identity, function lookup, a caller edge, and decompilation.
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.decompiler.DecompiledFunction;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.lang.Register;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class ReadOnlyTargetedQuery extends ghidra.app.script.GhidraScript {
    @Override
    public void run() throws Exception {
        Long targetRva = null;
        Long addressRva = null;
        Long displacementQuery = null;
        Long vtableSlot = null;
        List<Long> vtableRttiRvas = null;
        Long pointerTableRva = null;
        int pointerTableCount = 0;
        int directCallLimit = 0;
        int incomingCallLimit = 0;
        boolean enumerateCallEdges = false;
        String stringQuery = null;
        String[] scriptArgs = getScriptArgs();
        if (scriptArgs.length > 4) throw new IllegalArgumentException("Too many read-only query arguments");
        if (scriptArgs.length >= 1) {
            String token = scriptArgs[0].trim();
            if (token.startsWith("string:")) {
                stringQuery = token.substring("string:".length());
                if (!stringQuery.matches("[A-Za-z0-9_.$:]{1,128}")) {
                    throw new IllegalArgumentException("String query must contain 1-128 ASCII identifier characters");
                }
                if (scriptArgs.length != 1) throw new IllegalArgumentException("Literal search accepts no other query arguments");
            } else if (token.startsWith("offset:")) {
                String value = token.substring("offset:".length());
                if (value.startsWith("0x") || value.startsWith("0X")) value = value.substring(2);
                displacementQuery = Long.parseLong(value, 16);
                if (displacementQuery < 0) throw new IllegalArgumentException("Displacement must be non-negative");
                if (scriptArgs.length != 1) throw new IllegalArgumentException("Displacement search accepts no other query arguments");
            } else if (token.startsWith("pointer-table:")) {
                String value = token.substring("pointer-table:".length());
                if (value.startsWith("0x") || value.startsWith("0X")) value = value.substring(2);
                pointerTableRva = Long.parseLong(value, 16);
                if (pointerTableRva < 0) throw new IllegalArgumentException("Pointer-table RVA must be non-negative");
            } else if (token.startsWith("vtable-rtti:")) {
                vtableRttiRvas = new ArrayList<Long>();
                String value = token.substring("vtable-rtti:".length());
                for (String part : value.split(",")) {
                    String address = part.trim();
                    if (address.startsWith("0x") || address.startsWith("0X")) address = address.substring(2);
                    long parsed = Long.parseLong(address, 16);
                    if (parsed < 0) throw new IllegalArgumentException("Vtable RTTI RVA must be non-negative");
                    vtableRttiRvas.add(parsed);
                }
                if (vtableRttiRvas.size() < 1 || vtableRttiRvas.size() > 32) {
                    throw new IllegalArgumentException("Vtable RTTI census must contain 1-32 RVAs");
                }
                if (scriptArgs.length != 1) throw new IllegalArgumentException("Vtable RTTI census accepts no other query arguments");
            } else if (token.startsWith("address:")) {
                String value = token.substring("address:".length());
                if (value.startsWith("0x") || value.startsWith("0X")) value = value.substring(2);
                addressRva = Long.parseLong(value, 16);
                if (addressRva < 0) throw new IllegalArgumentException("Address RVA must be non-negative");
            } else {
                if (token.startsWith("0x") || token.startsWith("0X")) token = token.substring(2);
                targetRva = Long.parseLong(token, 16);
                if (targetRva < 0) throw new IllegalArgumentException("RVA must be non-negative");
            }
        }
        for (int i = 1; i < scriptArgs.length; i++) {
            String token = scriptArgs[i].trim();
            if (token.startsWith("slot:")) {
                String value = token.substring("slot:".length());
                if (value.startsWith("0x") || value.startsWith("0X")) value = value.substring(2);
                vtableSlot = Long.parseLong(value, 16);
                if (vtableSlot < 0 || vtableSlot > 0x10000) throw new IllegalArgumentException("Vtable slot is out of range");
            } else if (token.startsWith("calls:")) {
                directCallLimit = Integer.parseInt(token.substring("calls:".length()));
                if (directCallLimit < 0 || directCallLimit > 8) throw new IllegalArgumentException("Direct-call limit is out of range");
            } else if (token.startsWith("callers:")) {
                incomingCallLimit = Integer.parseInt(token.substring("callers:".length()));
                if (incomingCallLimit < 0 || incomingCallLimit > 32) throw new IllegalArgumentException("Incoming-caller limit is out of range");
            } else if (token.equals("edges:all")) {
                enumerateCallEdges = true;
            } else if (token.startsWith("pointer-count:")) {
                pointerTableCount = Integer.parseInt(token.substring("pointer-count:".length()));
                if (pointerTableCount < 1 || pointerTableCount > 128) throw new IllegalArgumentException("Pointer-table count must be between 1 and 128");
            } else {
                throw new IllegalArgumentException("Unknown read-only query argument: " + token);
            }
        }
        if (directCallLimit > 0 && targetRva == null) throw new IllegalArgumentException("Direct-call tracing requires an RVA target");
        if (incomingCallLimit > 0 && targetRva == null) throw new IllegalArgumentException("Incoming-caller tracing requires an RVA target");
        if (enumerateCallEdges && targetRva == null) throw new IllegalArgumentException("Direct-call edge census requires an RVA target");
        if (addressRva != null && (targetRva != null || stringQuery != null || pointerTableRva != null || vtableSlot != null || directCallLimit > 0 || incomingCallLimit > 0 || enumerateCallEdges)) {
            throw new IllegalArgumentException("Address-context query cannot be combined with other query modes");
        }
        if ((pointerTableRva == null) != (pointerTableCount == 0)) throw new IllegalArgumentException("Pointer-table RVA and count must be supplied together");
        if (pointerTableRva != null && (targetRva != null || stringQuery != null || vtableSlot != null || directCallLimit > 0 || incomingCallLimit > 0 || enumerateCallEdges)) {
            throw new IllegalArgumentException("Pointer-table query cannot be combined with other query modes");
        }

        FunctionManager manager = currentProgram.getFunctionManager();
        println("PROGRAM_NAME=" + currentProgram.getName());
        println("PROGRAM_EXECUTABLE_PATH=" + currentProgram.getExecutablePath());
        println("PROGRAM_LANGUAGE=" + currentProgram.getLanguageID());
        println("PROGRAM_COMPILER=" + currentProgram.getCompilerSpec().getCompilerSpecID());
        println("PROGRAM_IMAGE_BASE=" + currentProgram.getImageBase());
        long functionCount = 0;
        FunctionIterator functions = manager.getFunctions(true);
        while (functions.hasNext()) {
            functions.next();
            functionCount++;
        }
        println("FUNCTION_COUNT=" + functionCount);

        if (stringQuery != null) {
            searchLiteral(stringQuery, manager);
            return;
        }

        if (displacementQuery != null) {
            searchDisplacement(displacementQuery.longValue(), manager);
            return;
        }

        if (vtableRttiRvas != null) {
            for (int index = 0; index < vtableRttiRvas.size(); index++) {
                long rva = vtableRttiRvas.get(index).longValue();
                Address tableAddress = currentProgram.getImageBase().add(rva);
                println("VTABLE_RTTI_CENSUS_ENTRY=index:" + index + " requested_rva:0x" + Long.toHexString(rva).toUpperCase());
                printVtableRtti(tableAddress);
            }
            println("VTABLE_RTTI_CENSUS_COMPLETE=true");
            return;
        }

        if (addressRva != null) {
            Address targetAddress = currentProgram.getImageBase().add(addressRva.longValue());
            println("ADDRESS_RVA=0x" + Long.toHexString(addressRva.longValue()).toUpperCase());
            println("ADDRESS_TARGET=" + targetAddress);
            boolean addressInMemory = currentProgram.getMemory().contains(targetAddress);
            println("ADDRESS_MEMORY_CONTAINS=" + addressInMemory);
            Function containingFunction = manager.getFunctionContaining(targetAddress);
            println("ADDRESS_FUNCTION_LOOKUP=" + (containingFunction == null ? "<no-function>" :
                    containingFunction.getName() + " @ " + containingFunction.getEntryPoint()));
            ReferenceIterator addressReferences = currentProgram.getReferenceManager().getReferencesTo(targetAddress);
            int addressReferenceCount = 0;
            while (addressReferences.hasNext()) {
                Reference reference = addressReferences.next();
                Function sourceFunction = manager.getFunctionContaining(reference.getFromAddress());
                String sourceName = sourceFunction == null ? "<no-function>" : sourceFunction.getName() + " @ " + sourceFunction.getEntryPoint();
                println("ADDRESS_TARGET_XREF=from:" + reference.getFromAddress() + " type:" + reference.getReferenceType() +
                        " function:" + sourceName);
                addressReferenceCount++;
            }
            println("ADDRESS_TARGET_XREF_COUNT=" + addressReferenceCount);
            Instruction contextBefore = currentProgram.getListing().getInstructionBefore(targetAddress);
            int beforeCount = 0;
            while (contextBefore != null && beforeCount < 16) {
                println("ADDRESS_CONTEXT_BEFORE=" + contextBefore.getAddress() + " " +
                        contextBefore.getMnemonicString() + " " + contextBefore.toString());
                contextBefore = currentProgram.getListing().getInstructionBefore(contextBefore.getAddress());
                beforeCount++;
            }
            Instruction context = currentProgram.getListing().getInstructionAt(targetAddress);
            int instructionCount = 0;
            while (context != null && instructionCount < 128) {
                println("ADDRESS_CONTEXT_INSTRUCTION=" + context.getAddress() + " " +
                        context.getMnemonicString() + " " + context.toString());
                for (Reference reference : currentProgram.getReferenceManager().getReferencesFrom(context.getAddress())) {
                    if (!reference.getReferenceType().isCall()) continue;
                    Function callee = manager.getFunctionContaining(reference.getToAddress());
                    String calleeName = callee == null ? "<no-function>" : callee.getName() + " @ " + callee.getEntryPoint();
                    println("ADDRESS_DIRECT_CALL_EDGE=" + context.getAddress() + " -> " + reference.getToAddress() +
                            " target=" + calleeName);
                }
                context = currentProgram.getListing().getInstructionAfter(context.getAddress());
                instructionCount++;
            }
            println("ADDRESS_CONTEXT_INSTRUCTION_COUNT=" + instructionCount);
            println("ADDRESS_CONTEXT_COMPLETE=" + addressInMemory);
            return;
        }

        if (pointerTableRva != null) {
            Address tableAddress = currentProgram.getImageBase().add(pointerTableRva.longValue());
            println("POINTER_TABLE_BASE_RVA=0x" + Long.toHexString(pointerTableRva.longValue()).toUpperCase());
            println("POINTER_TABLE_BASE_ADDRESS=" + tableAddress);
            println("POINTER_TABLE_REQUESTED_COUNT=" + pointerTableCount);
            int tableReferenceCount = 0;
            for (int entryIndex = 0; entryIndex < pointerTableCount; entryIndex++) {
                Address entryAddress = tableAddress.add(entryIndex * 8L);
                ReferenceIterator tableReferences = currentProgram.getReferenceManager().getReferencesTo(entryAddress);
                while (tableReferences.hasNext()) {
                    Reference reference = tableReferences.next();
                    Function sourceFunction = manager.getFunctionContaining(reference.getFromAddress());
                    String sourceName = sourceFunction == null ? "<no-function>" : sourceFunction.getName() + " @ " + sourceFunction.getEntryPoint();
                    Instruction sourceInstruction = currentProgram.getListing().getInstructionAt(reference.getFromAddress());
                    String instructionText = sourceInstruction == null ? "<no-instruction>" :
                            sourceInstruction.getMnemonicString() + " " + sourceInstruction.toString();
                    println("POINTER_TABLE_XREF=entry_index:" + entryIndex + " entry_address:" + entryAddress +
                            " from:" + reference.getFromAddress() + " type:" + reference.getReferenceType() +
                            " function:" + sourceName + " instruction:" + instructionText);
                    if (sourceFunction == null && sourceInstruction != null) {
                        Instruction contextBefore = currentProgram.getListing().getInstructionBefore(reference.getFromAddress());
                        for (int contextIndex = 0; contextIndex < 8 && contextBefore != null; contextIndex++) {
                            println("POINTER_TABLE_XREF_CONTEXT=before:" + contextBefore.getAddress() + " " +
                                    contextBefore.getMnemonicString() + " " + contextBefore.toString());
                            contextBefore = currentProgram.getListing().getInstructionBefore(contextBefore.getAddress());
                        }
                        Instruction contextAfter = sourceInstruction;
                        for (int contextIndex = 0; contextIndex < 32 && contextAfter != null; contextIndex++) {
                            println("POINTER_TABLE_XREF_CONTEXT=at_or_after:" + contextAfter.getAddress() + " " +
                                    contextAfter.getMnemonicString() + " " + contextAfter.toString());
                            contextAfter = currentProgram.getListing().getInstructionAfter(contextAfter.getAddress());
                        }
                    }
                    tableReferenceCount++;
                }
            }
            println("POINTER_TABLE_XREF_COUNT=" + tableReferenceCount);
            println("POINTER_TABLE_XREF_SCAN_COMPLETE=true");
            int readCount = 0;
            for (int index = 0; index < pointerTableCount; index++) {
                Address entryAddress = tableAddress.add(index * 8L);
                try {
                    long pointer = currentProgram.getMemory().getLong(entryAddress);
                    Address targetAddress = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(pointer);
                    Function targetFunction = manager.getFunctionContaining(targetAddress);
                    String targetName = targetFunction == null ? "<no-function>" : targetFunction.getName() + " @ " + targetFunction.getEntryPoint();
                    println("POINTER_TABLE_ENTRY=index:" + index + " address:" + entryAddress +
                            " value:0x" + Long.toUnsignedString(pointer, 16).toUpperCase() +
                            " target:" + targetAddress + " function:" + targetName);
                    readCount++;
                } catch (Exception exception) {
                    println("POINTER_TABLE_ENTRY=index:" + index + " address:" + entryAddress +
                            " read_error:" + exception.getClass().getSimpleName());
                }
            }
            println("POINTER_TABLE_READ_COUNT=" + readCount);
            println("POINTER_TABLE_SCAN_COMPLETE=" + (readCount == pointerTableCount));
            return;
        }

        Function sample = null;
        if (targetRva != null) {
            Address targetAddress = currentProgram.getImageBase().add(targetRva.longValue());
            if (vtableSlot != null) {
                Address vtableAddress = targetAddress;
                Address slotAddress = vtableAddress.add(vtableSlot.longValue() * 8L);
                long pointer = currentProgram.getMemory().getLong(slotAddress);
                targetAddress = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(pointer);
                println("VTABLE_BASE_RVA=0x" + Long.toHexString(targetRva.longValue()).toUpperCase());
                println("VTABLE_SLOT_INDEX=0x" + Long.toHexString(vtableSlot.longValue()).toUpperCase());
                println("VTABLE_SLOT_ADDRESS=" + slotAddress);
                println("VTABLE_SLOT_TARGET_ADDRESS=" + targetAddress);
                println("VTABLE_SLOT_TARGET_RVA=0x" + Long.toHexString(targetAddress.subtract(currentProgram.getImageBase())).toUpperCase());
                println("VTABLE_RTTI_QUERY_RVA=0x" + Long.toHexString(targetRva.longValue()).toUpperCase());
                printVtableRtti(vtableAddress);
            }
            println("TARGET_RVA=0x" + Long.toHexString(targetAddress.subtract(currentProgram.getImageBase())).toUpperCase());
            println("TARGET_ADDRESS=" + targetAddress);
            sample = manager.getFunctionContaining(targetAddress);
            if (sample == null) throw new IllegalStateException("No existing function contains the requested RVA");
        } else {
            functions = manager.getFunctions(true);
            while (functions.hasNext()) {
                Function candidate = functions.next();
                if (!candidate.isThunk() && !candidate.isExternal()) {
                    sample = candidate;
                    break;
                }
            }
        }
        if (sample == null) throw new IllegalStateException("No analyzed non-thunk function is available");
        println("FUNCTION_LOOKUP=" + sample.getName() + " @ " + sample.getEntryPoint());

        Function[] outgoingCallees = new Function[16];
        int outgoingCount = 0;
        if (directCallLimit > 0) {
            InstructionIterator callInstructions = currentProgram.getListing().getInstructions(sample.getBody(), true);
            while (callInstructions.hasNext() && outgoingCount < directCallLimit &&
                   outgoingCount < outgoingCallees.length) {
                Instruction instruction = callInstructions.next();
                for (Reference reference : currentProgram.getReferenceManager().getReferencesFrom(instruction.getAddress())) {
                    if (!reference.getReferenceType().isCall()) continue;
                    Function callee = manager.getFunctionContaining(reference.getToAddress());
                    if (callee == null || callee.isThunk() || callee.equals(sample)) continue;
                    boolean duplicate = false;
                    for (int i = 0; i < outgoingCount; i++) {
                        if (outgoingCallees[i].equals(callee)) duplicate = true;
                    }
                    if (duplicate) continue;
                    outgoingCallees[outgoingCount++] = callee;
                    println("OUTGOING_CALL_EDGE=" + instruction.getAddress() + " -> " + reference.getToAddress() +
                            " target=" + callee.getName() + " @ " + callee.getEntryPoint());
                    if (outgoingCount >= directCallLimit) break;
                }
            }
            println("OUTGOING_CALL_COUNT=" + outgoingCount);
        }

        if (enumerateCallEdges) {
            int directEdgeCount = 0;
            int indirectCallSiteCount = 0;
            int callInstructionCount = 0;
            InstructionIterator callSites = currentProgram.getListing().getInstructions(sample.getBody(), true);
            while (callSites.hasNext()) {
                Instruction instruction = callSites.next();
                if (!instruction.getFlowType().isCall()) continue;
                callInstructionCount++;
                int directReferencesAtSite = 0;
                for (Reference reference : currentProgram.getReferenceManager().getReferencesFrom(instruction.getAddress())) {
                    if (!reference.getReferenceType().isCall()) continue;
                    directReferencesAtSite++;
                    Function callee = manager.getFunctionContaining(reference.getToAddress());
                    String calleeDescription = callee == null ? "<unresolved>" : callee.getName() + " @ " + callee.getEntryPoint();
                    println("OUTGOING_DIRECT_CALL_EDGE=" + instruction.getAddress() + " -> " + reference.getToAddress() +
                            " target=" + calleeDescription);
                    directEdgeCount++;
                }
                if (directReferencesAtSite == 0) {
                    StringBuilder operands = new StringBuilder();
                    for (int i = 0; i < instruction.getNumOperands(); i++) {
                        if (i > 0) operands.append(", ");
                        operands.append(instruction.getDefaultOperandRepresentation(i));
                    }
                    println("INDIRECT_CALL_SITE=" + instruction.getAddress() + " " +
                            instruction.getMnemonicString() + " " + operands);
                    indirectCallSiteCount++;
                }
            }
            println("OUTGOING_DIRECT_CALL_EDGE_COUNT=" + directEdgeCount);
            println("INDIRECT_CALL_SITE_COUNT=" + indirectCallSiteCount);
            println("CALL_INSTRUCTION_COUNT=" + callInstructionCount);
            println("DIRECT_CALL_EDGE_SCAN_COMPLETE=true");
        }

        int disassemblyCount = 0;
        InstructionIterator instructions = currentProgram.getListing().getInstructions(sample.getBody(), true);
        int disassemblyLimit = targetRva == null ? 24 : 512;
        while (instructions.hasNext() && disassemblyCount < disassemblyLimit) {
            Instruction instruction = instructions.next();
            StringBuilder operands = new StringBuilder();
            for (int i = 0; i < instruction.getNumOperands(); i++) {
                if (i > 0) operands.append(", ");
                operands.append(instruction.getDefaultOperandRepresentation(i));
            }
            println("DISASM=" + instruction.getAddress() + " " + instruction.getMnemonicString() + " " + operands);
            disassemblyCount++;
        }
        println("DISASSEMBLY_INSTRUCTION_COUNT=" + disassemblyCount);

        Function caller = null;
        Reference chosen = null;
        int incomingCallCount = 0;
        Function[] incomingCallers = new Function[64];
        int incomingCallerFunctionCount = 0;
        ReferenceIterator incoming = currentProgram.getReferenceManager().getReferencesTo(sample.getEntryPoint());
        while (incoming.hasNext()) {
            Reference reference = incoming.next();
            if (!reference.getReferenceType().isCall()) continue;
            Function source = manager.getFunctionContaining(reference.getFromAddress());
            if (source == null || source.isThunk()) continue;
            incomingCallCount++;
            if (incomingCallCount <= 256) {
                println("XREF_CALL_EDGE=" + reference.getFromAddress() + " -> " + reference.getToAddress() +
                        " caller=" + source.getName() + " @ " + source.getEntryPoint() +
                        " target=" + sample.getName() + " @ " + sample.getEntryPoint());
            }
            if (chosen == null) {
                caller = source;
                chosen = reference;
            }
            boolean duplicateCaller = false;
            for (int i = 0; i < incomingCallerFunctionCount; i++) {
                if (incomingCallers[i].equals(source)) duplicateCaller = true;
            }
            if (!duplicateCaller && incomingCallerFunctionCount < incomingCallers.length) {
                incomingCallers[incomingCallerFunctionCount++] = source;
            }
        }
        println("XREF_CALL_COUNT=" + incomingCallCount);
        println("INCOMING_CALLER_FUNCTION_COUNT=" + incomingCallerFunctionCount);
        if (incomingCallCount > 256) println("XREF_CALL_EDGE_OUTPUT_LIMIT=256");
        if (chosen == null) {
            println("XREF_CALL_EDGE=NOT_FOUND_IN_ANALYZED_PROJECT");
        }

        int incomingReferenceCount = 0;
        ReferenceIterator allIncoming = currentProgram.getReferenceManager().getReferencesTo(sample.getEntryPoint());
        while (allIncoming.hasNext()) {
            Reference reference = allIncoming.next();
            incomingReferenceCount++;
            if (incomingReferenceCount <= 256) {
                Function source = manager.getFunctionContaining(reference.getFromAddress());
                String sourceFunction = source == null ? "<none>" : source.getName() + " @ " + source.getEntryPoint();
                Data sourceData = currentProgram.getListing().getDataAt(reference.getFromAddress());
                String sourceDataDescription = sourceData == null ? "<none>" :
                        sourceData.getDataType().getName() + "=" + String.valueOf(sourceData.getValue());
                StringBuilder words = new StringBuilder();
                for (int offset = -8; offset <= 16; offset += 4) {
                    if (words.length() > 0) words.append(",");
                    Address wordAddress = reference.getFromAddress().add(offset);
                    try {
                        words.append(wordAddress).append(":0x").append(
                                String.format("%08X", currentProgram.getMemory().getInt(wordAddress)));
                    } catch (Exception ignored) {
                        words.append(wordAddress).append(":<unreadable>");
                    }
                }
                println("XREF_ANY=" + reference.getFromAddress() + " -> " + reference.getToAddress() +
                        " type=" + reference.getReferenceType() + " source=" + sourceFunction +
                        " data=" + sourceDataDescription + " words=" + words);
                ReferenceIterator sourceUsers = currentProgram.getReferenceManager().getReferencesTo(reference.getFromAddress());
                int sourceUserCount = 0;
                while (sourceUsers.hasNext()) {
                    Reference sourceUser = sourceUsers.next();
                    sourceUserCount++;
                    if (sourceUserCount <= 64) {
                        Function userFunction = manager.getFunctionContaining(sourceUser.getFromAddress());
                        String userFunctionName = userFunction == null ? "<none>" :
                                userFunction.getName() + " @ " + userFunction.getEntryPoint();
                        println("XREF_ANY_SOURCE_USER=" + sourceUser.getFromAddress() + " -> " +
                                sourceUser.getToAddress() + " type=" + sourceUser.getReferenceType() +
                                " function=" + userFunctionName);
                    }
                }
                println("XREF_ANY_SOURCE_USER_COUNT=" + sourceUserCount + " target=" + reference.getFromAddress());
                if (sourceUserCount > 64) println("XREF_ANY_SOURCE_USER_OUTPUT_LIMIT=64 target=" + reference.getFromAddress());
            }
        }
        println("XREF_ANY_COUNT=" + incomingReferenceCount);
        if (incomingReferenceCount > 256) println("XREF_ANY_OUTPUT_LIMIT=256");

        DecompInterface decompiler = new DecompInterface();
        try {
            if (!decompiler.openProgram(currentProgram)) throw new IllegalStateException("DecompInterface could not open current program");
            DecompileResults result = decompiler.decompileFunction(sample, 90, monitor);
            if (!result.decompileCompleted()) throw new IllegalStateException("Decompilation did not complete: " + result.getErrorMessage());
            DecompiledFunction decompiled = result.getDecompiledFunction();
            println("DECOMPILATION_BEGIN=" + sample.getName());
            println(decompiled.getC());
            println("DECOMPILATION_END=" + sample.getName());
            if (chosen != null && caller != null && !caller.equals(sample)) {
                DecompileResults callerResult = decompiler.decompileFunction(caller, 90, monitor);
                if (callerResult.decompileCompleted()) {
                    DecompiledFunction callerFunction = callerResult.getDecompiledFunction();
                    println("CALLER_DECOMPILATION_BEGIN=" + caller.getName() + " @ " + caller.getEntryPoint());
                    println(callerFunction.getC());
                    println("CALLER_DECOMPILATION_END=" + caller.getName());
                }
            }
            for (int i = 0; i < outgoingCount; i++) {
                DecompileResults calleeResult = decompiler.decompileFunction(outgoingCallees[i], 90, monitor);
                if (!calleeResult.decompileCompleted()) continue;
                DecompiledFunction calleeFunction = calleeResult.getDecompiledFunction();
                println("CALLEE_DECOMPILATION_BEGIN=" + outgoingCallees[i].getName() + " @ " + outgoingCallees[i].getEntryPoint());
                println(calleeFunction.getC());
                println("CALLEE_DECOMPILATION_END=" + outgoingCallees[i].getName());
            }
            int decompiledIncomingCount = 0;
            for (int i = 0; i < incomingCallerFunctionCount && decompiledIncomingCount < incomingCallLimit; i++) {
                Function incomingCaller = incomingCallers[i];
                if (incomingCaller.equals(caller)) continue;
                DecompileResults incomingResult = decompiler.decompileFunction(incomingCaller, 90, monitor);
                if (!incomingResult.decompileCompleted()) continue;
                DecompiledFunction incomingFunction = incomingResult.getDecompiledFunction();
                println("INCOMING_CALLER_DECOMPILATION_BEGIN=" + incomingCaller.getName() + " @ " + incomingCaller.getEntryPoint());
                println(incomingFunction.getC());
                println("INCOMING_CALLER_DECOMPILATION_END=" + incomingCaller.getName());
                decompiledIncomingCount++;
            }
            println("INCOMING_CALLER_DECOMPILED_COUNT=" + decompiledIncomingCount);
        } finally {
            decompiler.dispose();
        }
    }

    private void printVtableRtti(Address vtableAddress) {
        try {
            Address colPointerAddress = vtableAddress.subtract(8);
            long colPointer = currentProgram.getMemory().getLong(colPointerAddress);
            Address colAddress = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(colPointer);
            int signature = currentProgram.getMemory().getInt(colAddress);
            int offset = currentProgram.getMemory().getInt(colAddress.add(4));
            int typeDescriptorRva = currentProgram.getMemory().getInt(colAddress.add(12));
            println("VTABLE_RTTI_TABLE_RVA=0x" + Long.toHexString(vtableAddress.subtract(currentProgram.getImageBase())).toUpperCase());
            println("VTABLE_RTTI_COL_ADDRESS=" + colAddress);
            println("VTABLE_RTTI_SIGNATURE=0x" + Integer.toHexString(signature).toUpperCase());
            println("VTABLE_RTTI_SUBOBJECT_OFFSET=" + offset + "/0x" + Integer.toHexString(offset).toUpperCase());
            if (signature == 1) {
                Address typeDescriptor = currentProgram.getImageBase().add(Integer.toUnsignedLong(typeDescriptorRva));
                byte[] nameBytes = new byte[256];
                int count = currentProgram.getMemory().getBytes(typeDescriptor.add(16), nameBytes);
                int nameLength = 0;
                while (nameLength < count && nameBytes[nameLength] != 0) nameLength++;
                println("VTABLE_RTTI_TYPE_DESCRIPTOR_RVA=0x" + Long.toHexString(Integer.toUnsignedLong(typeDescriptorRva)).toUpperCase());
                println("VTABLE_RTTI_TYPE_NAME=" + new String(nameBytes, 0, nameLength, StandardCharsets.UTF_8));
            }
        } catch (Exception exception) {
            println("VTABLE_RTTI_READ_ERROR=" + exception.getClass().getSimpleName());
        }
    }

    private void searchDisplacement(long displacement, FunctionManager manager) throws Exception {
        final int accessOutputLimit = 2048;
        final int writerFunctionLimit = 16;
        final int callerOutputLimit = 256;
        long instructionCount = 0;
        long accessCount = 0;
        long stackAccessCount = 0;
        int accessPrinted = 0;
        int callerPrinted = 0;
        List<Function> writerFunctions = new ArrayList<>();
        List<Function> computedWriterFunctions = new ArrayList<>();
        List<Function> matchedFunctions = new ArrayList<>();
        List<Function> visitorOwnerFunctions = new ArrayList<>();
        List<Function> visitorCallees = new ArrayList<>();
        List<Function> vtableMethods = new ArrayList<>();
        println("OFFSET_QUERY=0x" + Long.toHexString(displacement).toUpperCase());

        InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = instructions.next();
            instructionCount++;
            Function owner = manager.getFunctionContaining(instruction.getAddress());
            for (int operandIndex = 0; operandIndex < instruction.getNumOperands(); operandIndex++) {
                boolean displacementMatches = false;
                boolean hasObjectRegister = false;
                boolean hasStackRegister = false;
                for (Object operand : instruction.getOpObjects(operandIndex)) {
                    if (operand instanceof Scalar && ((Scalar)operand).getUnsignedValue() == displacement) {
                        displacementMatches = true;
                    } else if (operand instanceof Register) {
                        String registerName = ((Register)operand).getName().toUpperCase();
                        if (registerName.equals("RBP") || registerName.equals("EBP") ||
                                registerName.equals("BP") || registerName.equals("RSP") ||
                                registerName.equals("ESP") || registerName.equals("SP")) {
                            hasStackRegister = true;
                        } else {
                            hasObjectRegister = true;
                        }
                    }
                }
                if (!displacementMatches || (!hasObjectRegister && !hasStackRegister)) continue;
                if (!hasObjectRegister && hasStackRegister) {
                    stackAccessCount++;
                    continue;
                }

                accessCount++;
                boolean destinationOperandCandidate = operandIndex == 0 && isLikelyMemoryWriteMnemonic(instruction.getMnemonicString());
                if (owner != null && !matchedFunctions.contains(owner)) matchedFunctions.add(owner);
                if (destinationOperandCandidate && owner != null && !writerFunctions.contains(owner)) {
                    writerFunctions.add(owner);
                }
                if (operandIndex == 0 && instruction.getMnemonicString().equalsIgnoreCase("CALL")) {
                    StringBuilder linearContext = new StringBuilder();
                    Instruction contextInstruction = instruction;
                    for (int contextIndex = 0; contextIndex < 9 && contextInstruction != null; contextIndex++) {
                        if (contextIndex > 0) linearContext.append(" || ");
                        linearContext.append(contextInstruction.getAddress()).append(" ")
                                .append(contextInstruction.toString());
                        contextInstruction = contextInstruction.getPrevious();
                    }
                    String ownerDescription = owner == null ? "<no-function>" :
                            owner.getName() + " @ " + owner.getEntryPoint();
                    println("OFFSET_INDIRECT_CALLSITE_CONTEXT=address:" + instruction.getAddress() +
                            " rva:0x" + Long.toHexString(instruction.getAddress().subtract(currentProgram.getImageBase())).toUpperCase() +
                            " function:" + ownerDescription +
                            " operand:" + instruction.getDefaultOperandRepresentation(operandIndex) +
                            " linear_context_reverse:" + linearContext);
                }
                if (destinationOperandCandidate && owner != null &&
                        instruction.getMnemonicString().equalsIgnoreCase("MOVSS") &&
                        !computedWriterFunctions.contains(owner)) {
                    computedWriterFunctions.add(owner);
                }
                if (accessPrinted < accessOutputLimit) {
                    String ownerDescription = owner == null ? "<no-function>" :
                            owner.getName() + " @ " + owner.getEntryPoint();
                    println("OFFSET_ACCESS=address:" + instruction.getAddress() +
                            " rva:0x" + Long.toHexString(instruction.getAddress().subtract(currentProgram.getImageBase())).toUpperCase() +
                            " function:" + ownerDescription +
                            " operand_index:" + operandIndex +
                            " destination_operand_candidate:" + destinationOperandCandidate +
                            " operand:" + instruction.getDefaultOperandRepresentation(operandIndex) +
                            " instruction:" + instruction.toString());
                    accessPrinted++;
                }
            }
        }
        println("OFFSET_INSTRUCTION_COUNT=" + instructionCount);
        println("OFFSET_ACCESS_COUNT=" + accessCount);
        println("OFFSET_STACK_ACCESS_COUNT=" + stackAccessCount);
        println("OFFSET_ACCESSES_PRINTED=" + accessPrinted);
        if (accessCount > accessOutputLimit) println("OFFSET_ACCESS_OUTPUT_LIMIT=" + accessOutputLimit);
        println("OFFSET_MATCHED_FUNCTION_COUNT=" + matchedFunctions.size());
        println("OFFSET_WRITER_CANDIDATE_FUNCTION_COUNT=" + writerFunctions.size());
        println("OFFSET_COMPUTED_WRITER_FUNCTION_COUNT=" + computedWriterFunctions.size());
        for (Function function : writerFunctions) {
            println("OFFSET_WRITER_CANDIDATE=" + function.getName() + " @ " + function.getEntryPoint() +
                    " RVA=0x" + Long.toHexString(function.getEntryPoint().subtract(currentProgram.getImageBase())).toUpperCase());
        }

        SymbolIterator symbolIterator = currentProgram.getSymbolTable().getAllSymbols(true);
        int visitorSymbolCount = 0;
        int visitorVtableCount = 0;
        while (symbolIterator.hasNext()) {
            Symbol symbol = symbolIterator.next();
            String symbolName = symbol.getName();
            if (!symbolName.contains("ArmorRatingVisitor")) continue;
            visitorSymbolCount++;
            println("OFFSET_VISITOR_SYMBOL=" + symbolName + " address:" + symbol.getAddress() +
                    " type:" + symbol.getSymbolType());
            if (!symbolName.toLowerCase().contains("vftable")) continue;
            visitorVtableCount++;
            for (int entryIndex = 0; entryIndex < 16; entryIndex++) {
                Address entryAddress = symbol.getAddress().add(entryIndex * 8L);
                try {
                    long pointer = currentProgram.getMemory().getLong(entryAddress);
                    Address targetAddress = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(pointer);
                    Function targetFunction = manager.getFunctionContaining(targetAddress);
                    String targetDescription = targetFunction == null ? "<no-function>" :
                            targetFunction.getName() + " @ " + targetFunction.getEntryPoint();
                    println("OFFSET_VISITOR_VTABLE_ENTRY=index:" + entryIndex + " address:" + entryAddress +
                            " target:" + targetAddress + " function:" + targetDescription);
                } catch (Exception exception) {
                    println("OFFSET_VISITOR_VTABLE_ENTRY=index:" + entryIndex + " address:" + entryAddress +
                            " read_error:" + exception.getClass().getSimpleName());
                }
            }
            ReferenceIterator symbolReferences = currentProgram.getReferenceManager().getReferencesTo(symbol.getAddress());
            while (symbolReferences.hasNext()) {
                Reference reference = symbolReferences.next();
                Function owner = manager.getFunctionContaining(reference.getFromAddress());
                String ownerDescription = owner == null ? "<no-function>" : owner.getName() + " @ " + owner.getEntryPoint();
                println("OFFSET_VISITOR_VTABLE_XREF=from:" + reference.getFromAddress() +
                        " type:" + reference.getReferenceType() + " function:" + ownerDescription);
                if (owner != null && !visitorOwnerFunctions.contains(owner)) visitorOwnerFunctions.add(owner);
            }
        }
        println("OFFSET_VISITOR_SYMBOL_COUNT=" + visitorSymbolCount);
        println("OFFSET_VISITOR_VTABLE_COUNT=" + visitorVtableCount);
        println("OFFSET_VISITOR_OWNER_FUNCTION_COUNT=" + visitorOwnerFunctions.size());
        println("OFFSET_VISITOR_SYMBOL_SCAN_COMPLETE=true");

        println("OFFSET_SCAN_COMPLETE=true");

        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        try {
            int writerCount = Math.min(writerFunctionLimit, writerFunctions.size());
            for (int index = 0; index < writerCount; index++) {
                Function function = writerFunctions.get(index);
                println("OFFSET_WRITER_ANALYSIS_BEGIN=" + function.getName() + " @ " + function.getEntryPoint());
                InstructionIterator bodyInstructions = currentProgram.getListing().getInstructions(function.getBody(), true);
                long bodyCount = 0;
                while (bodyInstructions.hasNext()) {
                    bodyInstructions.next();
                    bodyCount++;
                }
                println("OFFSET_WRITER_BODY_INSTRUCTION_COUNT=" + bodyCount);
                ReferenceIterator incoming = currentProgram.getReferenceManager().getReferencesTo(function.getEntryPoint());
                int functionCallerCount = 0;
                while (incoming.hasNext()) {
                    Reference reference = incoming.next();
                    if (!reference.getReferenceType().isCall()) continue;
                    functionCallerCount++;
                    if (callerPrinted < callerOutputLimit) {
                        Function caller = manager.getFunctionContaining(reference.getFromAddress());
                        String callerDescription = caller == null ? "<no-function>" : caller.getName() + " @ " + caller.getEntryPoint();
                        println("OFFSET_WRITER_CALLER=" + reference.getFromAddress() + " -> " +
                                reference.getToAddress() + " caller:" + callerDescription);
                        callerPrinted++;
                    }
                }
                println("OFFSET_WRITER_CALLER_COUNT=" + functionCallerCount);
                DecompileResults result = decompiler.decompileFunction(function, 90, monitor);
                if (result.decompileCompleted() && result.getDecompiledFunction() != null) {
                    DecompiledFunction decompiled = result.getDecompiledFunction();
                    println("OFFSET_WRITER_DECOMPILATION_BEGIN=" + function.getName() + " @ " + function.getEntryPoint());
                    println(decompiled.getC());
                    println("OFFSET_WRITER_DECOMPILATION_END=" + function.getName());
                } else {
                    println("OFFSET_WRITER_DECOMPILATION_FAILED=" + function.getName() + " error:" + result.getErrorMessage());
                }
                println("OFFSET_WRITER_ANALYSIS_END=" + function.getName());
            }
            if (writerFunctions.size() > writerFunctionLimit) {
                println("OFFSET_WRITER_FUNCTION_OUTPUT_LIMIT=" + writerFunctionLimit);
            }
            if (callerPrinted >= callerOutputLimit) println("OFFSET_WRITER_CALLER_OUTPUT_LIMIT=" + callerOutputLimit);

            for (Function visitorOwner : visitorOwnerFunctions) {
                InstructionIterator ownerInstructions = currentProgram.getListing().getInstructions(visitorOwner.getBody(), true);
                while (ownerInstructions.hasNext()) {
                    Instruction instruction = ownerInstructions.next();
                    if (!instruction.getFlowType().isCall()) continue;
                    for (Reference reference : currentProgram.getReferenceManager().getReferencesFrom(instruction.getAddress())) {
                        if (!reference.getReferenceType().isCall()) continue;
                        Function callee = manager.getFunctionContaining(reference.getToAddress());
                        if (callee == null || callee.isThunk() || callee.equals(visitorOwner)) continue;
                        println("OFFSET_VISITOR_OWNER_CALL=" + visitorOwner.getName() + " @ " + visitorOwner.getEntryPoint() +
                                " site:" + instruction.getAddress() + " target:" + callee.getName() + " @ " + callee.getEntryPoint());
                        if (!visitorCallees.contains(callee)) visitorCallees.add(callee);
                    }
                }
            }
            int visitorCalleeLimit = Math.min(8, visitorCallees.size());
            for (int index = 0; index < visitorCalleeLimit; index++) {
                Function callee = visitorCallees.get(index);
                DecompileResults result = decompiler.decompileFunction(callee, 90, monitor);
                if (result.decompileCompleted() && result.getDecompiledFunction() != null) {
                    println("OFFSET_VISITOR_CALLEE_DECOMPILATION_BEGIN=" + callee.getName() + " @ " + callee.getEntryPoint());
                    println(result.getDecompiledFunction().getC());
                    println("OFFSET_VISITOR_CALLEE_DECOMPILATION_END=" + callee.getName());
                } else {
                    println("OFFSET_VISITOR_CALLEE_DECOMPILATION_FAILED=" + callee.getName() + " error:" + result.getErrorMessage());
                }
            }
            println("OFFSET_VISITOR_CALLEE_ANALYSIS_COMPLETE=true");
            if (visitorCallees.size() > 8) println("OFFSET_VISITOR_CALLEE_OUTPUT_LIMIT=8");

            List<Function> computedWriterCallees = new ArrayList<>();
            int computedWriterCount = Math.min(8, computedWriterFunctions.size());
            for (int writerIndex = 0; writerIndex < computedWriterCount; writerIndex++) {
                Function writer = computedWriterFunctions.get(writerIndex);
                println("OFFSET_COMPUTED_WRITER_ANALYSIS_BEGIN=" + writer.getName() + " @ " + writer.getEntryPoint());
                InstructionIterator writerInstructions = currentProgram.getListing().getInstructions(writer.getBody(), true);
                int writerInstructionCount = 0;
                while (writerInstructions.hasNext()) {
                    Instruction instruction = writerInstructions.next();
                    writerInstructionCount++;
                    println("OFFSET_COMPUTED_WRITER_DISASM=" + instruction.getAddress() + " " + instruction.toString());
                    for (Reference reference : currentProgram.getReferenceManager().getReferencesFrom(instruction.getAddress())) {
                        if (reference.getReferenceType().isCall()) {
                            Function callee = manager.getFunctionContaining(reference.getToAddress());
                            String calleeDescription = callee == null ? "<no-function>" : callee.getName() + " @ " + callee.getEntryPoint();
                            println("OFFSET_COMPUTED_WRITER_CALL=" + instruction.getAddress() + " -> " +
                                    reference.getToAddress() + " target:" + calleeDescription);
                            if (callee != null && !callee.isThunk() && !callee.equals(writer) &&
                                    !computedWriterCallees.contains(callee)) computedWriterCallees.add(callee);
                            continue;
                        }

                        Address tableBase = reference.getToAddress();
                        String targetDescription = "<no-function>";
                        Function referencedFunction = manager.getFunctionContaining(tableBase);
                        if (referencedFunction != null) targetDescription = referencedFunction.getName() + " @ " + referencedFunction.getEntryPoint();
                        println("OFFSET_COMPUTED_WRITER_DATA_REF=from:" + instruction.getAddress() +
                                " to:" + tableBase + " type:" + reference.getReferenceType() + " target:" + targetDescription);
                        if (!currentProgram.getMemory().contains(tableBase)) continue;

                        long[] values = new long[16];
                        boolean[] readable = new boolean[16];
                        int functionTargetCount = 0;
                        List<Function> tableFunctions = new ArrayList<>();
                        for (int entryIndex = 0; entryIndex < 16; entryIndex++) {
                            Address entryAddress = tableBase.add(entryIndex * 8L);
                            try {
                                values[entryIndex] = currentProgram.getMemory().getLong(entryAddress);
                                readable[entryIndex] = true;
                                Address entryTarget = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(values[entryIndex]);
                                Function method = manager.getFunctionContaining(entryTarget);
                                if (method != null) {
                                    functionTargetCount++;
                                    if (!method.isThunk() && !tableFunctions.contains(method)) tableFunctions.add(method);
                                }
                            } catch (Exception exception) {
                                readable[entryIndex] = false;
                            }
                        }
                        if (functionTargetCount < 3) continue;
                        println("OFFSET_COMPUTED_WRITER_DATA_TABLE_CANDIDATE=base:" + tableBase +
                                " function_targets:" + functionTargetCount);
                        for (int entryIndex = 0; entryIndex < 16; entryIndex++) {
                            if (!readable[entryIndex]) continue;
                            Address entryTarget = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(values[entryIndex]);
                            Function method = manager.getFunctionContaining(entryTarget);
                            String methodDescription = method == null ? "<no-function>" : method.getName() + " @ " + method.getEntryPoint();
                            println("OFFSET_COMPUTED_WRITER_DATA_TABLE_ENTRY=index:" + entryIndex +
                                    " address:" + tableBase.add(entryIndex * 8L) + " target:" + entryTarget +
                                    " function:" + methodDescription);
                            if (method != null && !method.isThunk() && !vtableMethods.contains(method)) vtableMethods.add(method);
                        }
                    }
                }
                println("OFFSET_COMPUTED_WRITER_INSTRUCTION_COUNT=" + writerInstructionCount);
                println("OFFSET_COMPUTED_WRITER_ANALYSIS_END=" + writer.getName());
            }
            if (computedWriterFunctions.size() > 8) println("OFFSET_COMPUTED_WRITER_FUNCTION_OUTPUT_LIMIT=8");

            int computedCalleeLimit = Math.min(12, computedWriterCallees.size());
            for (int index = 0; index < computedCalleeLimit; index++) {
                Function callee = computedWriterCallees.get(index);
                DecompileResults result = decompiler.decompileFunction(callee, 90, monitor);
                if (result.decompileCompleted() && result.getDecompiledFunction() != null) {
                    println("OFFSET_COMPUTED_WRITER_CALLEE_DECOMPILATION_BEGIN=" + callee.getName() + " @ " + callee.getEntryPoint());
                    println(result.getDecompiledFunction().getC());
                    println("OFFSET_COMPUTED_WRITER_CALLEE_DECOMPILATION_END=" + callee.getName());
                } else {
                    println("OFFSET_COMPUTED_WRITER_CALLEE_DECOMPILATION_FAILED=" + callee.getName() + " error:" + result.getErrorMessage());
                }
            }
            if (computedWriterCallees.size() > 12) println("OFFSET_COMPUTED_WRITER_CALLEE_OUTPUT_LIMIT=12");

            int vtableMethodLimit = Math.min(12, vtableMethods.size());
            for (int index = 0; index < vtableMethodLimit; index++) {
                Function method = vtableMethods.get(index);
                DecompileResults result = decompiler.decompileFunction(method, 90, monitor);
                if (result.decompileCompleted() && result.getDecompiledFunction() != null) {
                    println("OFFSET_VISITOR_METHOD_DECOMPILATION_BEGIN=" + method.getName() + " @ " + method.getEntryPoint());
                    println(result.getDecompiledFunction().getC());
                    println("OFFSET_VISITOR_METHOD_DECOMPILATION_END=" + method.getName());
                } else {
                    println("OFFSET_VISITOR_METHOD_DECOMPILATION_FAILED=" + method.getName() + " error:" + result.getErrorMessage());
                }
            }
            println("OFFSET_COMPUTED_WRITER_ANALYSIS_COMPLETE=true");
            println("OFFSET_VISITOR_METHOD_ANALYSIS_COMPLETE=true");
            if (vtableMethods.size() > 12) println("OFFSET_VISITOR_METHOD_OUTPUT_LIMIT=12");
        } finally {
            decompiler.dispose();
        }
        println("OFFSET_WRITER_ANALYSIS_COMPLETE=true");
    }

    private boolean isLikelyMemoryWriteMnemonic(String mnemonic) {
        String upper = mnemonic.toUpperCase();
        return upper.equals("MOV") || upper.equals("MOVSS") || upper.equals("MOVSD") ||
                upper.equals("MOVAPS") || upper.equals("MOVUPS") || upper.equals("MOVDQA") ||
                upper.equals("MOVDQU") || upper.equals("MOVD") || upper.equals("MOVQ") ||
                upper.equals("ADD") || upper.equals("SUB") || upper.equals("AND") ||
                upper.equals("OR") || upper.equals("XOR") || upper.equals("INC") ||
                upper.equals("DEC") || upper.equals("NEG") || upper.equals("NOT") ||
                upper.equals("XCHG") || upper.equals("CMPXCHG") || upper.equals("XADD") ||
                upper.equals("BTS") || upper.equals("BTR") || upper.equals("BTC") ||
                upper.equals("ADDSS") || upper.equals("ADDSD") || upper.equals("SUBSS") ||
                upper.equals("SUBSD") || upper.equals("MULSS") || upper.equals("MULSD") ||
                upper.equals("DIVSS") || upper.equals("DIVSD") || upper.equals("STOS") ||
                upper.equals("STOSB") || upper.equals("STOSW") || upper.equals("STOSD") ||
                upper.equals("STOSQ");
    }

    private void searchLiteral(String query, FunctionManager manager) throws Exception {
        byte[] needle = query.getBytes(StandardCharsets.US_ASCII);
        final int chunkSize = 65536;
        final int matchOutputLimit = 256;
        final int referenceOutputLimit = 512;
        byte[] readBuffer = new byte[chunkSize];
        long matchCount = 0;
        long referenceCount = 0;
        int matchPrinted = 0;
        int referencePrinted = 0;
        println("STRING_QUERY=" + query);

        for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
            if (!block.isInitialized()) continue;
            long blockSize = block.getSize();
            long offset = 0;
            byte[] tail = new byte[0];
            while (offset < blockSize) {
                monitor.checkCancelled();
                int requestLength = (int)Math.min((long)readBuffer.length, blockSize - offset);
                int bytesRead = currentProgram.getMemory().getBytes(block.getStart().add(offset), readBuffer, 0, requestLength);
                if (bytesRead != requestLength) {
                    throw new IllegalStateException("Incomplete initialized memory read at " + block.getStart().add(offset));
                }
                byte[] combined = new byte[tail.length + bytesRead];
                System.arraycopy(tail, 0, combined, 0, tail.length);
                System.arraycopy(readBuffer, 0, combined, tail.length, bytesRead);
                long combinedStart = offset - tail.length;
                for (int index = 0; index <= combined.length - needle.length; index++) {
                    boolean equal = true;
                    for (int n = 0; n < needle.length; n++) {
                        if (combined[index + n] != needle[n]) {
                            equal = false;
                            break;
                        }
                    }
                    if (!equal) continue;

                    Address matchAddress = block.getStart().add(combinedStart + index);
                    matchCount++;
                    if (matchPrinted < matchOutputLimit) {
                        Data data = currentProgram.getListing().getDataAt(matchAddress);
                        String dataDescription = data == null ? "<none>" :
                                data.getDataType().getName() + "=" + String.valueOf(data.getValue());
                        println("STRING_MATCH=" + matchAddress + " RVA=0x" +
                                Long.toHexString(matchAddress.subtract(currentProgram.getImageBase())).toUpperCase() +
                                " block=" + block.getName() + " data=" + dataDescription);
                        matchPrinted++;
                    }
                    ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(matchAddress);
                    while (references.hasNext()) {
                        Reference reference = references.next();
                        referenceCount++;
                        if (referencePrinted < referenceOutputLimit) {
                            Function source = manager.getFunctionContaining(reference.getFromAddress());
                            String sourceFunction = source == null ? "<none>" : source.getName() + " @ " + source.getEntryPoint();
                            println("STRING_REFERENCE=" + reference.getFromAddress() + " -> " + reference.getToAddress() +
                                    " type=" + reference.getReferenceType() + " function=" + sourceFunction);
                            referencePrinted++;
                        }
                    }
                }
                int keep = Math.min(needle.length - 1, combined.length);
                tail = Arrays.copyOfRange(combined, combined.length - keep, combined.length);
                offset += bytesRead;
            }
        }
        println("STRING_MATCH_COUNT=" + matchCount);
        println("STRING_MATCHES_PRINTED=" + matchPrinted);
        if (matchCount > matchOutputLimit) println("STRING_MATCH_OUTPUT_LIMIT=" + matchOutputLimit);
        println("STRING_SCAN_COMPLETE=true");
        println("STRING_REFERENCE_COUNT=" + referenceCount);
        println("STRING_REFERENCES_PRINTED=" + referencePrinted);
        if (referenceCount > referenceOutputLimit) println("STRING_REFERENCE_OUTPUT_LIMIT=" + referenceOutputLimit);
        println("STRING_REFERENCE_SCAN_COMPLETE=true");
    }
}
