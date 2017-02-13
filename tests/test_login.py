from output_viewer.diagsviewer import DiagnosticsViewerClient


dvc = DiagnosticsViewerClient("http://pcmdi10.llnl.gov:8008", cert=False)
for _ in range(100):
    dvc.login("btest", "test")
