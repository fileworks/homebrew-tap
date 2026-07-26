# url + sha256 are rewritten by .github/workflows/bump.yml on every release
# of the CLI — do not edit them by hand.
class ImmichExport < Formula
  include Language::Python::Virtualenv

  desc "Export everything out of Immich into a plain, human-readable folder tree"
  homepage "https://github.com/fileworks/immich-export"
  url "https://files.pythonhosted.org/packages/5a/94/43bb78eafcab06ac265dda459da311a7bda1bf3be9b4f24a6ba534037d8d/immich_export-0.0.4.tar.gz"
  sha256 "45d3c3fcdfd80e4b0a0396c6d3dba57595e7499b58274f2db46297e4ed97f375"
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
           "immich-export==#{version}"
    bin.install_symlink libexec/"bin/immich-export"
  end

  test do
    assert_match "immich-export", shell_output("#{bin}/immich-export --version")
  end
end
