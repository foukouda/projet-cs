// main.js
const { app, BrowserWindow } = require('electron');
const { exec } = require('child_process');

let pythonProcess;

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
  });

  win.loadURL('http://localhost:5000');
}

app.whenReady().then(() => {
  // Lancer le serveur Python
  pythonProcess = exec('python app.py', (error, stdout, stderr) => {
    if (error) {
      console.error(`Erreur d'exécution du script Python: ${error}`);
      return;
    }
    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);
  });

  createWindow();
});

app.on('window-all-closed', () => {
  // Fermer le processus Python lorsque l'application Electron est fermée
  if (pythonProcess) pythonProcess.kill();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
