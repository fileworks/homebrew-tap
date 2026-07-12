# NOTE: url/sha256/version pin are placeholders until the first PyPI release;
# .github/workflows/bump.yml rewrites them on every release of the CLI.
class PaperlessExport < Formula
  include Language::Python::Virtualenv

  desc "Paperless-ngx export wrapper + _Steuer/YYYY tax view"
  homepage "https://github.com/fileworks/paperless-export"
  url "https://files.pythonhosted.org/packages/source/p/paperless-export/paperless_export-0.0.0.tar.gz"
  sha256 "0000000000000000000000000000000000000000000000000000000000000000"
  license "MIT"

  depends_on "python@3.12"

  def install
    venv = virtualenv_create(libexec, "python3.12")
    # Personal-tap pattern: pip-install the pinned release with its deps
    # instead of vendoring every dependency as a resource block.
    system libexec/"bin/pip", "install", "--no-cache-dir", "paperless-export[pdf]==#{version}"
    bin.install_symlink libexec/"bin/paperless-export"
  end

  test do
    assert_match "paperless-export", shell_output("#{bin}/paperless-export --version")
  end
end
