// Enable folder selection on the folder upload input (Dash 2.x).
(function () {
    function enableFolderPicker() {
        const upload = document.getElementById("ingest-folder-upload");
        if (!upload) {
            return;
        }

        const input = upload.querySelector('input[type="file"]');
        if (!input || input.dataset.folderEnabled === "true") {
            return;
        }

        input.setAttribute("webkitdirectory", "");
        input.setAttribute("directory", "");
        input.setAttribute("multiple", "");
        input.dataset.folderEnabled = "true";
    }

    enableFolderPicker();

    const observer = new MutationObserver(enableFolderPicker);
    observer.observe(document.body, { childList: true, subtree: true });
})();
