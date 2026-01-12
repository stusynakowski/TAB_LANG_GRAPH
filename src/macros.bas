REM  *****  BASIC  *****
Option Explicit

' Helper function to load Python scripts
Public Function GetPythonScript(macro As String, Optional location As String) As Object
    If IsMissing(location) Then location = "user"
    Dim mspf As Object
    Dim sp As Object
    Dim uri As String
    If location="document" Then
        sp = ThisComponent.getScriptProvider()
    Else
        mspf = CreateUnoService("com.sun.star.script.provider.MasterScriptProviderFactory")
        sp = mspf.createScriptProvider("")
    End If
    uri = "vnd.sun.star.script:"& macro &"?language=Python&location="& location
    GetPythonScript = sp.getScript(uri)
End Function

' Main Entry Point
Public Function FSF(workflow_name As String, Optional a1, Optional a2, Optional a3, Optional a4, Optional a5) As Variant
    On Error GoTo ErrorHandler
    Dim script As Object
    ' Note: Requires 'spreadsheet_addin.py' to be installed as 'fsf_bridge.py'
    script = GetPythonScript("fsf_bridge.py$FSF", "user")
    
    Dim args() As Variant
    Dim tempArgs() As Variant
    tempArgs = Array(a1, a2, a3, a4, a5)
    
    ' Build dynamic arguments array
    Dim count As Integer
    count = 0
    Dim i As Integer
    
    ' Count provided arguments
    For i = 0 To 4
        If Not IsMissing(tempArgs(i)) Then
            count = count + 1
        End If
    Next i
    
    ' Create minimal array
    ReDim args(count) As Variant
    args(0) = workflow_name
    
    Dim current As Integer
    current = 1
    For i = 0 To 4
        If Not IsMissing(tempArgs(i)) Then
            args(current) = tempArgs(i)
            current = current + 1
        End If
    Next i
    
    FSF = script.invoke(args, Array(), Array())
    Exit Function

ErrorHandler:
    FSF = "Basic Error: " & Error()
End Function
