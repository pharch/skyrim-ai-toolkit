unit ResearchRecordQuery;
{
Hotkey: Ctrl+Alt+F9

Targeted, read-only native record export for the isolated five-master SSEView
session. The recursive field walker and TSV schema are derived from the
authoritative LEGACY_SKYRIM_REPO/scripts/xedit/export-records.pas
(source SHA-256 c88d86d9550d203f359a63c6118dc2fb4528d0493262c9cd08f5f8514878b1e4).
This script enumerates exactly one named record in the loaded official masters;
it does not create or modify a plugin.
}
var rows: TStringList;

function Clean(s: string): string;
begin
  s := StringReplace(s, #9, ' ', [rfReplaceAll]);
  s := StringReplace(s, #13, ' ', [rfReplaceAll]);
  Result := StringReplace(s, #10, ' ', [rfReplaceAll]);
end;

function IsOfficialPlugin(const p: string): Boolean;
begin
  Result := SameText(p, 'Skyrim.esm') or SameText(p, 'Update.esm') or
    SameText(p, 'Dawnguard.esm') or SameText(p, 'HearthFires.esm') or
    SameText(p, 'Dragonborn.esm');
end;

procedure Walk(e: IInterface; prefix, fieldPath: string);
var i: Integer; child, target: IInterface; value, link: string;
begin
  value := GetEditValue(e);
  link := '';
  target := LinksTo(e);
  if Assigned(target) then
    link := GetFileName(GetFile(target)) + ':' + IntToHex(GetLoadOrderFormID(target), 8);
  rows.Add(prefix + #9 + Clean(fieldPath) + #9 + Clean(value) + #9 + Clean(link));
  for i := 0 to ElementCount(e) - 1 do begin
    child := ElementByIndex(e, i);
    Walk(child, prefix, fieldPath + '\' + IntToStr(i) + ':' + Name(child));
  end;
end;

function Initialize: Integer;
var i, j, found: Integer; f, g, r: IInterface; p, prefix: string; seen, status: TStringList;
begin
  // Match the authoritative global exporter: all work happens in Initialize,
  // then returning 1 prevents xEdit from traversing a GUI selection.
  Result := 1;
  if FileExists(__OUTPUT__) then begin
    AddMessage('Refusing to overwrite an existing native export.');
    Exit;
  end;

  seen := TStringList.Create;
  for i := 0 to FileCount - 1 do begin
    p := GetFileName(FileByIndex(i));
    seen.Add(p);
  end;
  seen.SaveToFile(__LOADED__);

  for i := 0 to seen.Count - 1 do begin
    p := seen[i];
    if SameText(p, 'SkyrimSE.exe') then Continue;
    if not IsOfficialPlugin(p) then begin
      AddMessage('Refusing unexpected loaded plugin: ' + p);
      status := TStringList.Create;
      status.Add('status=BLOCKED');
      status.Add('reason=unexpected_loaded_plugin:' + Clean(p));
      status.SaveToFile(__STATUS__);
      status.Free;
      seen.Free;
      Exit;
    end;
  end;
  if (seen.IndexOf('Skyrim.esm') < 0) or (seen.IndexOf('Update.esm') < 0) or
     (seen.IndexOf('Dawnguard.esm') < 0) or (seen.IndexOf('HearthFires.esm') < 0) or
     (seen.IndexOf('Dragonborn.esm') < 0) then begin
    AddMessage('Refusing export: all five official masters must be loaded.');
    status := TStringList.Create;
    status.Add('status=BLOCKED');
    status.Add('reason=official_master_missing');
    status.SaveToFile(__STATUS__);
    status.Free;
    seen.Free;
    Exit;
  end;
  seen.Free;

  rows := TStringList.Create;
  rows.Add('source_plugin' + #9 + 'form_id' + #9 + 'editor_id' + #9 + 'signature' + #9 + 'winning_plugin' + #9 + 'field_path' + #9 + 'value' + #9 + 'links_to');
  found := 0;
  f := nil;
  for i := 0 to FileCount - 1 do
    if SameText(GetFileName(FileByIndex(i)), __PLUGIN__) then
      f := FileByIndex(i);
  if not Assigned(f) then begin
    AddMessage('Requested source plugin is not loaded.');
    rows.Free;
    rows := nil;
    Result := 1;
    Exit;
  end;

  g := GroupBySignature(f, __SIGNATURE__);
  if Assigned(g) then
    for j := 0 to ElementCount(g) - 1 do begin
      r := ElementByIndex(g, j);
      if SameText(EditorID(r), __EDITOR_ID__) then begin
        prefix := GetFileName(GetFile(r)) + #9 + IntToHex(GetLoadOrderFormID(r), 8) + #9 +
          Clean(EditorID(r)) + #9 + Signature(r) + #9 + GetFileName(GetFile(WinningOverride(r)));
        Walk(r, prefix, Signature(r));
        Inc(found);
      end;
    end;

  if found <> 1 then begin
    AddMessage('Expected exactly one named record; found ' + IntToStr(found));
    status := TStringList.Create;
    status.Add('status=NOT_FOUND');
    status.Add('matches=' + IntToStr(found));
    status.SaveToFile(__STATUS__);
    status.Free;
    rows.Free;
    rows := nil;
    Exit;
  end;
  rows.SaveToFile(__OUTPUT__);
  rows.Free;
  rows := nil;
  status := TStringList.Create;
  status.Add('status=PASS');
  status.Add('matches=1');
  status.SaveToFile(__STATUS__);
  status.Free;
  AddMessage('NATIVE_RECORD_QUERY_MATCHES=1');
end;
end.
