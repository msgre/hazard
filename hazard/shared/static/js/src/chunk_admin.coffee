"""
Inicializace editoru Codemirror.
"""

$(document).ready () ->
    editor = CodeMirror.fromTextArea(document.getElementById("id_content"), {
        mode: "text/html"
        tabMode: "indent"
        lineWrapping: true
        gutter: true
        lineNumbers: true
    })
