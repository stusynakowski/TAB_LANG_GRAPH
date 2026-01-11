REM  *****  BASIC  *****
Option Explicit

' Helper function from the documentation to load Python scripts
Public Function GetPythonScript(macro As String, _
        Optional location As String) As com.sun.star.script.provider.Xscript
    If IsMissing(location) Then location = "user" ' Assumes script is in user profile
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

' Your Wrapper Function for use in Cells: =FSF("Echo"; "Hello") (Note: check if your locale uses ; or ,)
Public Function FSF(workflow_name As String, Optional arg1) As Variant
    On Error GoTo ErrorHandler
    Dim script As Object
    ' Update: You placed the file in the OS Application directory (Shared), named 'fsf_bridge.py'
    script = GetPythonScript("fsf_bridge.py$FSF", "user")
    
    Dim args() As Variant
    
    ' Handle arguments (Basic to Python mapping)
    ' Fix: Removed 'As String' from Optional arg1 so IsMissing works correctly
    If IsMissing(arg1) Then
        args = Array(workflow_name)
    Else
        args = Array(workflow_name, arg1)
    End If
    
    ' Invoke the Python function
    ' returns the result from Python
    FSF = script.invoke(args, Array(), Array())
    Exit Function

ErrorHandler:
    FSF = "Basic Error: " & Error()
End Function
