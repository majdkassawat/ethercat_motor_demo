using System;
using System.Diagnostics;
using System.IO;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using LibGit2Sharp;

namespace HardwareInterface
{
    /// <summary>
    /// Thin façade around your real‑world HW API.
    /// Replace the mock implementations with actual HW calls.
    /// </summary>
    public sealed class DeviceController : IDisposable
    {
        public ValueTask ConnectAsync()
        {
            Console.WriteLine("[HW] Connecting to robot…");
            // TODO: replace with real connection logic
            return ValueTask.CompletedTask;
        }

        public async ValueTask<string> RunSelfTestAsync()
        {
            Console.WriteLine("[HW] Running self‑test.");
            await Task.Delay(500); // simulate latency
            // TODO: collect real diagnostic output
            return "OK";
        }

        public async ValueTask<int> RunDemoAsync()
        {
            Console.WriteLine("[HW] Executing demo.py");
            var repoDir = Path.GetDirectoryName(Repository.Discover(Directory.GetCurrentDirectory())!);
            var psi = new ProcessStartInfo("python", Path.Combine(repoDir!, "demo.py"))
            {
                RedirectStandardOutput = true,
                RedirectStandardError  = true,
                UseShellExecute = false,
                WorkingDirectory = repoDir
            };
            using var proc = Process.Start(psi)!;
            string output = await proc.StandardOutput.ReadToEndAsync();
            string error  = await proc.StandardError.ReadToEndAsync();
            await proc.WaitForExitAsync();
            Console.WriteLine(output);
            if (!string.IsNullOrWhiteSpace(error))
                Console.Error.WriteLine(error);

            var m = Regex.Match(output, @"Actual position:\s*(\d+)");
            return m.Success ? int.Parse(m.Groups[1].Value) : -1;
        }

        public void Dispose() => Console.WriteLine("[HW] Disconnected.");
    }
}
