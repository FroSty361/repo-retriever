colorModeButton = document.getElementById('colorModeButton');
colorModeButton.onclick = changeColorMode;

function init()
{
    const visited = JSON.parse(localStorage.getItem("visited"));

    if (visited === null || visited === "false")
    {
        const browserIsDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

        localStorage.setItem("is-dark-mode", browserIsDarkMode.toString());
    }

    localStorage.setItem("visited", "true");

    changeUIColors(localStorage.getItem("is-dark-mode"));
}

function changeColorMode()
{
    const isDarkMode = localStorage.getItem("is-dark-mode");

    if (isDarkMode === "true") // Set To Light
    {
        localStorage.setItem("is-dark-mode", "false");
    }
    else // Set To Dark
    {
        localStorage.setItem("is-dark-mode", "true");
    }

    changeUIColors(localStorage.getItem("is-dark-mode"));
}

function changeUIColors(isDarkMode)
{
    if (isDarkMode === "true")
    {
        if (document.documentElement.classList.contains('dark-mode') === false)
        {
            document.documentElement.classList.add('dark-mode');
        }

        colorModeButton.innerText = "Set To Light";
    }
    else
    {
        if (document.documentElement.classList.contains('dark-mode') === true)
        {
            document.documentElement.classList.remove('dark-mode');
        }

        colorModeButton.innerText = "Set To Dark";
    }
}

init();