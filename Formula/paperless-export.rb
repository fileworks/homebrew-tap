# url + sha256 are rewritten by .github/workflows/bump.yml on every release
# of the CLI — do not edit them by hand.
class PaperlessExport < Formula
  include Language::Python::Virtualenv

  desc "Paperless-ngx export wrapper + _Steuer/YYYY tax view"
  homepage "https://github.com/fileworks/paperless-export"
  url "https://files.pythonhosted.org/packages/62/7a/4b00ed7085bd96fac108d28d24f141060876ebf9360f6e0b4e0e5a16a71f/paperless_export-1.0.0.tar.gz"
  sha256 "0b1337d77506dfa0cf221fd737fb4a46bd3e64b8fc7adcca6ac5db4b7c4a59ea"
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
