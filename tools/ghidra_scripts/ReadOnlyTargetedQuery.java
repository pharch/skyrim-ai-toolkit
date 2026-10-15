// Read-only proof of program identity, function lookup, a caller edge, and decompilation.
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.decompiler.DecompiledFunction;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class ReadOnlyTargetedQuery extends ghidra.app.script.GhidraScript {
    @Override
    public void run() throws Exception {
        Long targetRva = null;
        String[] scriptArgs = getScriptArgs();
        if (scriptArgs.length > 1) throw new IllegalArgumentException("Expected at most one RVA script argument");
        if (scriptArgs.length == 1) {
            String token = scriptArgs[0].trim();
            if (token.startsWith("0x") || token.startsWith("0X")) token = token.substring(2);
            targetRva = Long.parseLong(token, 16);
            if (targetRva < 0) throw new IllegalArgumentException("RVA must be non-negative");
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

        Function sample = null;
        if (targetRva != null) {
            Address targetAddress = currentProgram.getImageBase().add(targetRva.longValue());
            println("TARGET_RVA=0x" + Long.toHexString(targetRva.longValue()).toUpperCase());
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

        int disassemblyCount = 0;
        InstructionIterator instructions = currentProgram.getListing().getInstructions(sample.getBody(), true);
        while (instructions.hasNext() && disassemblyCount < 24) {
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
        Function callee = null;
        Reference chosen = null;
        functions = manager.getFunctions(true);
        while (functions.hasNext() && chosen == null) {
            Function target = functions.next();
            if (targetRva != null && !target.equals(sample)) continue;
            if (target.isThunk()) continue;
            ReferenceIterator incoming = currentProgram.getReferenceManager().getReferencesTo(target.getEntryPoint());
            while (incoming.hasNext()) {
                Reference reference = incoming.next();
                if (!reference.getReferenceType().isCall()) continue;
                Function source = manager.getFunctionContaining(reference.getFromAddress());
                if (source == null || source.isThunk()) continue;
                caller = source;
                callee = target;
                chosen = reference;
                break;
            }
        }
        Function decompileTarget = sample;
        if (chosen == null) {
            println("XREF_CALL_EDGE=NOT_FOUND_IN_ANALYZED_PROJECT");
        } else {
            Address from = chosen.getFromAddress();
            Address to = chosen.getToAddress();
            println("XREF_CALL_EDGE=" + from + " -> " + to + " target=" + callee.getName() + " @ " + callee.getEntryPoint());
            decompileTarget = caller;
        }

        DecompInterface decompiler = new DecompInterface();
        try {
            if (!decompiler.openProgram(currentProgram)) throw new IllegalStateException("DecompInterface could not open current program");
            DecompileResults result = decompiler.decompileFunction(decompileTarget, 90, monitor);
            if (!result.decompileCompleted()) throw new IllegalStateException("Decompilation did not complete: " + result.getErrorMessage());
            DecompiledFunction decompiled = result.getDecompiledFunction();
            println("DECOMPILATION_BEGIN=" + decompileTarget.getName());
            println(decompiled.getC());
            println("DECOMPILATION_END=" + decompileTarget.getName());
        } finally {
            decompiler.dispose();
        }
    }
}
