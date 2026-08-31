async function downloadFile(pathEncoded, fileURLEncoded)
{
    const response = await fetch('/download-file/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            path: pathEncoded,
            file_url: fileURLEncoded
        })
    });

    if (response.ok === false)
    {
        alert('File Download failed');

        return;
    }

    const disposition = response.headers.get('Content-Disposition');
    let filename = "github_file";

    if (disposition && disposition.includes('filename=')){
      filename = disposition
        .split('filename=')[1]
        .split(';')[0]
        .replace(/['"]/g, '');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();

    a.remove();
    window.URL.revokeObjectURL(url);
}

async function downloadDirectory(pathEncoded, directoryURLEncoded)
{
    const response = await fetch('/download-directory/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            path: pathEncoded,
            directory_url: directoryURLEncoded
        })
    });

    if (response.ok === false)
    {
        alert('Directory Download failed');

        return;
    }

    const disposition = response.headers.get('Content-Disposition');
    let filename = "github_file";

    if (disposition && disposition.includes('filename=')){
      filename = disposition
        .split('filename=')[1]
        .split(';')[0]
        .replace(/['"]/g, '');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();

    a.remove();
    window.URL.revokeObjectURL(url);
}