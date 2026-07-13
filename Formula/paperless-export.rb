# url + sha256 are rewritten by .github/workflows/bump.yml on every release
# of the CLI — do not edit them by hand.
class PaperlessExport < Formula
  include Language::Python::Virtualenv

  desc "Paperless-ngx export wrapper + _Steuer/YYYY tax view"
  homepage "https://github.com/fileworks/paperless-export"
  url "https://files.pythonhosted.org/packages/50/e3/535ea7687ff6df374fab3eb661ecbba4ff3c19dbb99e5d587280c162656f/paperless_export-0.0.2.tar.gz"
  sha256 "5722d3884e290b3a03285e5d2e2fd614a43c3aa2ba03c1af55d1d6b5f051d43a"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_create(libexec, "python3.12")
    # virtualenv_create builds the venv with `--without-pip`, so libexec/bin/pip
    # does not exist and invoking it fails silently. Bootstrap pip first.
    system libexec/"bin/python", "-m", "ensurepip", "--upgrade"
    # Personal-tap pattern: pip-install the pinned release with its deps
    # instead of vendoring every dependency as a resource block.
    system libexec/"bin/python", "-m", "pip", "install", "--no-cache-dir",
           "paperless-export[pdf]==#{version}"
    bin.install_symlink libexec/"bin/paperless-export"
  end

  test do
    assert_match "paperless-export", shell_output("#{bin}/paperless-export --version")
  end
end
