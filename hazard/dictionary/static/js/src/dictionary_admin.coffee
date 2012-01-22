"""
Inicializace editoru Codemirror.
"""

$(document).ready () ->
    editor = CodeMirror.fromTextArea(document.getElementById("id_description"), {
        mode: "text/html"
        tabMode: "indent"
        lineWrapping: true
        gutter: true
        lineNumbers: true
    })
