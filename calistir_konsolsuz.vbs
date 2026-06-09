Dim shell, fso
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Dosyanın bulunduğu dizini al
Dim scriptDir
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' calistir.bat dosyasını arka planda (konsolsuz) çalıştır
shell.Run "cmd /c """ & scriptDir & "\calistir.bat""", 1, False

Set shell = Nothing
Set fso = Nothing
