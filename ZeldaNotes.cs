using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Threading;
using System.Windows.Forms;

namespace ZeldaNotesLauncher
{
    static class Program
    {
        private static Process serverProcess = null;
        private static NotifyIcon trayIcon = null;
        private static Process appWindowProcess = null;

        [STAThread]
        static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            bool isPopout = args.Length > 0 && args[0].ToLower().Contains("popout");
            bool isMinimized = args.Length > 0 && args[0].ToLower().Contains("minimized");

            // 1. Asegurar que el servidor local esté activo
            EnsureServerRunning();

            // 2. Configurar icono de bandeja del sistema (System Tray)
            SetupTrayIcon();

            // 3. Abrir la ventana nativa (salvo si inició minimizado)
            if (!isMinimized)
            {
                LaunchAppWindow(isPopout ? "http://localhost:8080/popout" : "http://localhost:8080");
            }

            // Ejecutar el bucle de mensajes de Windows
            Application.Run();
        }

        private static bool IsServerAlive()
        {
            try
            {
                HttpWebRequest req = (HttpWebRequest)WebRequest.Create("http://localhost:8080/api/status");
                req.Timeout = 1200;
                req.Method = "GET";
                using (HttpWebResponse resp = (HttpWebResponse)req.GetResponse())
                {
                    return resp.StatusCode == HttpStatusCode.OK;
                }
            }
            catch
            {
                return false;
            }
        }

        private static void EnsureServerRunning()
        {
            if (IsServerAlive())
            {
                return; // Ya está corriendo
            }

            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string pythonExe = ResolvePythonPath(baseDir);

            if (string.IsNullOrEmpty(pythonExe) || !File.Exists(pythonExe))
            {
                // Descarga automática silenciosa del runtime portable oficial de Python (10 MB)
                try
                {
                    string runtimeDir = Path.Combine(baseDir, "runtime");
                    string zipFile = Path.Combine(baseDir, "python-embed.zip");
                    string downloadUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip";

                    using (WebClient wc = new WebClient())
                    {
                        wc.DownloadFile(downloadUrl, zipFile);
                    }

                    if (!Directory.Exists(runtimeDir)) Directory.CreateDirectory(runtimeDir);
                    ZipFile.ExtractToDirectory(zipFile, runtimeDir);
                    if (File.Exists(zipFile)) File.Delete(zipFile);

                    pythonExe = Path.Combine(runtimeDir, "python.exe");
                }
                catch (Exception ex)
                {
                    MessageBox.Show("No se pudo iniciar el servidor ni descargar el entorno portable:\n" + ex.Message,
                        "Zelda Notes — Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }
            }

            string serverPy = Path.Combine(baseDir, "server.py");
            if (!File.Exists(serverPy))
            {
                // Bootstrapper: Si el usuario descargó solo el .exe suelto, auto-descargar el paquete oficial
                try
                {
                    string zipUrl = "https://github.com/LFR-SnowBall/zelda-notes/releases/download/v1.0.0/ZeldaNotes-v1.0.0-windows.zip";
                    string tempZip = Path.Combine(baseDir, "zelda-notes-install.zip");

                    using (WebClient wc = new WebClient())
                    {
                        wc.Headers.Add("User-Agent", "ZeldaNotes-Launcher");
                        wc.DownloadFile(zipUrl, tempZip);
                    }

                    ExtractZipSafely(tempZip, baseDir);
                    if (File.Exists(tempZip)) File.Delete(tempZip);

                    pythonExe = ResolvePythonPath(baseDir);
                }
                catch (Exception ex)
                {
                    MessageBox.Show("No se encontró 'server.py' en la carpeta y ocurrió un error al intentar la descarga automática:\n" + ex.Message,
                        "Zelda Notes — Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }
            }

            if (!File.Exists(serverPy))
            {
                MessageBox.Show("No se encontró 'server.py' en: " + baseDir,
                    "Zelda Notes — Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = pythonExe;
            psi.Arguments = "\"" + serverPy + "\"";
            psi.WorkingDirectory = baseDir;
            psi.CreateNoWindow = true;
            psi.WindowStyle = ProcessWindowStyle.Hidden;
            psi.UseShellExecute = false;

            try
            {
                serverProcess = Process.Start(psi);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error al ejecutar servidor:\n" + ex.Message, "Zelda Notes", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            // Esperar hasta que responda HTTP (máximo 4 segundos)
            for (int i = 0; i < 20; i++)
            {
                if (IsServerAlive()) break;
                Thread.Sleep(200);
            }
        }

        private static string ResolvePythonPath(string baseDir)
        {
            // 1. Runtime embebido en la misma carpeta
            string embedded = Path.Combine(baseDir, "runtime", "python.exe");
            if (File.Exists(embedded)) return embedded;

            // 2. Python de TotK-Recomp
            string localApp = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            string recompPy = Path.Combine(localApp, "Programs", "TotK-Recomp", "python", "python.exe");
            if (File.Exists(recompPy)) return recompPy;

            // 3. Python en PATH
            try
            {
                Process p = new Process();
                p.StartInfo.FileName = "where";
                p.StartInfo.Arguments = "python";
                p.StartInfo.UseShellExecute = false;
                p.StartInfo.RedirectStandardOutput = true;
                p.StartInfo.CreateNoWindow = true;
                p.Start();
                string output = p.StandardOutput.ReadLine();
                p.WaitForExit();
                if (!string.IsNullOrEmpty(output) && File.Exists(output.Trim()))
                {
                    return output.Trim();
                }
            }
            catch { }

            return null;
        }

        private static void LaunchAppWindow(string url)
        {
            // Buscar Microsoft Edge o Google Chrome para ejecutar en modo aplicación nativa (--app)
            string edgePath = @"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe";
            if (!File.Exists(edgePath)) edgePath = @"C:\Program Files\Microsoft\Edge\Application\msedge.exe";

            string chromePath = @"C:\Program Files\Google\Chrome\Application\chrome.exe";
            if (!File.Exists(chromePath)) chromePath = @"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe";

            string browserExe = File.Exists(edgePath) ? edgePath : (File.Exists(chromePath) ? chromePath : null);

            if (browserExe != null)
            {
                ProcessStartInfo psi = new ProcessStartInfo();
                psi.FileName = browserExe;
                psi.Arguments = string.Format("--app=\"{0}\" --window-size=1280,820", url);
                try
                {
                    appWindowProcess = Process.Start(psi);
                    return;
                }
                catch { }
            }

            // Fallback al navegador predeterminado
            try
            {
                Process.Start(url);
            }
            catch { }
        }

        private static void SetupTrayIcon()
        {
            trayIcon = new NotifyIcon();
            trayIcon.Text = "Purah Pad Companion — Zelda Notes";

            // Crear icono nativo de escudo / trifuerza en memoria
            Bitmap bmp = new Bitmap(16, 16);
            using (Graphics g = Graphics.FromImage(bmp))
            {
                g.Clear(Color.Transparent);
                using (Brush b = new SolidBrush(Color.FromArgb(0, 220, 255)))
                {
                    Point[] triangle = new Point[] {
                        new Point(8, 1),
                        new Point(15, 14),
                        new Point(1, 14)
                    };
                    g.FillPolygon(b, triangle);
                }
            }
            trayIcon.Icon = Icon.FromHandle(bmp.GetHicon());
            trayIcon.Visible = true;

            ContextMenu menu = new ContextMenu();
            menu.MenuItems.Add("🗡️ Abrir Purah Pad (Principal)", (s, e) => LaunchAppWindow("http://localhost:8080"));
            menu.MenuItems.Add("↗️ Abrir Ventana Flotante (Popout)", (s, e) => LaunchAppWindow("http://localhost:8080/popout"));
            menu.MenuItems.Add("-");
            menu.MenuItems.Add("📋 Copiar Enlace LAN (Móvil / Tablet)", (s, e) => {
                string ip = GetLocalIPAddress();
                Clipboard.SetText("http://" + ip + ":8080");
                trayIcon.ShowBalloonTip(2000, "Zelda Notes", "Enlace móvil copiado al portapapeles:\nhttp://" + ip + ":8080", ToolTipIcon.Info);
            });
            menu.MenuItems.Add("-");
            menu.MenuItems.Add("❌ Salir y Cerrar Servidor", (s, e) => ExitApplication());

            trayIcon.ContextMenu = menu;
            trayIcon.DoubleClick += (s, e) => LaunchAppWindow("http://localhost:8080");
        }

        private static string GetLocalIPAddress()
        {
            try
            {
                foreach (NetworkInterface ni in NetworkInterface.GetAllNetworkInterfaces())
                {
                    if (ni.OperationalStatus == OperationalStatus.Up &&
                        (ni.NetworkInterfaceType == NetworkInterfaceType.Wireless80211 || ni.NetworkInterfaceType == NetworkInterfaceType.Ethernet))
                    {
                        foreach (UnicastIPAddressInformation ip in ni.GetIPProperties().UnicastAddresses)
                        {
                            if (ip.Address.AddressFamily == AddressFamily.InterNetwork && !IPAddress.IsLoopback(ip.Address))
                            {
                                return ip.Address.ToString();
                            }
                        }
                    }
                }
            }
            catch { }
            return "localhost";
        }

        private static void ExtractZipSafely(string zipPath, string targetDir)
        {
            using (ZipArchive archive = ZipFile.OpenRead(zipPath))
            {
                foreach (ZipArchiveEntry entry in archive.Entries)
                {
                    string fullPath = Path.Combine(targetDir, entry.FullName);
                    if (string.IsNullOrEmpty(entry.Name))
                    {
                        if (!Directory.Exists(fullPath)) Directory.CreateDirectory(fullPath);
                        continue;
                    }

                    string dir = Path.GetDirectoryName(fullPath);
                    if (!Directory.Exists(dir)) Directory.CreateDirectory(dir);

                    if (entry.Name.Equals("ZeldaNotes.exe", StringComparison.OrdinalIgnoreCase))
                        continue;

                    entry.ExtractToFile(fullPath, true);
                }
            }
        }

        private static void ExitApplication()
        {
            if (trayIcon != null)
            {
                trayIcon.Visible = false;
                trayIcon.Dispose();
            }

            if (serverProcess != null && !serverProcess.HasExited)
            {
                try
                {
                    serverProcess.Kill();
                }
                catch { }
            }

            Application.Exit();
            Environment.Exit(0);
        }
    }
}
