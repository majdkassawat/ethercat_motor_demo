using LibGit2Sharp;
using System;
using System.Diagnostics;
using System.IO.Compression;
using System.Threading;

const string repoPath  = @"C:\Dev\CodexHardwareLoop";
const string remote    = "origin";
const string branch    = "main";
const string resultsBranchPrefix = "results/";

static bool Run(string exe, string args)
{
    var p = Process.Start(new ProcessStartInfo(exe, args)
    {
        RedirectStandardOutput = true,
        RedirectStandardError  = true,
        UseShellExecute = false
    })!;
    p.OutputDataReceived += (_, e) => Console.WriteLine(e.Data);
    p.ErrorDataReceived  += (_, e) => Console.Error.WriteLine(e.Data);
    p.BeginOutputReadLine();
    p.BeginErrorReadLine();
    p.WaitForExit();
    return p.ExitCode == 0;
}

Console.WriteLine("=== Codex HW Test Agent ===");

while (true)
{
    using var repo = new Repository(repoPath);
    var headBefore = repo.Head.Tip.Sha;

    Console.WriteLine("Fetching…");
    Commands.Fetch(repo, remote, Array.Empty<string>(), null, null);
    repo.Reset(ResetMode.Hard, repo.Branches[$"{remote}/{branch}"].Tip);

    var headAfter = repo.Head.Tip.Sha;
    if (headBefore == headAfter)
    {
        Console.WriteLine("No new commit. Sleeping 60 s.");
        Thread.Sleep(TimeSpan.FromSeconds(60));
        continue;
    }

    Console.ForegroundColor = ConsoleColor.Yellow;
    Console.Write($"New commit {headAfter[..7]} detected. Run integration tests now? [y/N] ");
    Console.ResetColor();
    if (Console.ReadKey().Key != ConsoleKey.Y) { Console.WriteLine(); continue; }
    Console.WriteLine();

    if (!Run("dotnet", $"test "{repoPath}\src\IntegrationTests\IntegrationTests.csproj" --configuration Release --no-build --results-directory TestResults --logger "trx""))
    {
        Console.WriteLine("dotnet test failed."); continue;
    }

    if (!Run("allure", "generate TestResults -o AllureReport --clean"))
    {
        Console.WriteLine("Allure CLI failed. Skipping publish."); continue;
    }

    var zipName = $"allure-{headAfter[..7]}.zip";
    if (File.Exists(zipName)) File.Delete(zipName);
    ZipFile.CreateFromDirectory("AllureReport", zipName, CompressionLevel.Fastest, false);

    var resultsBranchName = resultsBranchPrefix + headAfter;
    var rb = repo.Branches[resultsBranchName] ?? repo.CreateBranch(resultsBranchName);
    Commands.Checkout(repo, rb);

    File.Copy(zipName, Path.Combine(repo.Info.WorkingDirectory, zipName), true);
    if (repo.Index.Add(zipName) != null)
    {
        repo.Index.Write();
        var author = new Signature("HW‑Runner", "hw@dummy.local", DateTimeOffset.Now);
        repo.Commit($"Add Allure report for {headAfter[..7]}", author, author);
        repo.Network.Push(rb, new PushOptions());
    }

    Commands.Checkout(repo, branch);
}
