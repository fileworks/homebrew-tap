# url + sha256 are rewritten by .github/workflows/bump.yml on every release
# of the CLI — do not edit them by hand.
class PaperlessExport < Formula
  include Language::Python::Virtualenv

  desc "Paperless-ngx export wrapper + _Steuer/YYYY tax view"
  homepage "https://github.com/fileworks/paperless-export"
  url "https://files.pythonhosted.org/packages/ca/7d/963c511f39e05696584f1dc540e56aa1977b2e449bf2c973cfc48590eed7/paperless_export-0.0.3.tar.gz"
  sha256 "6c81906d908ec2cbb248c4a0ce2795f9a64bcce8733b6231ab802106079523f9"
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
