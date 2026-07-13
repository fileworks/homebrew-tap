# url + sha256 are rewritten by .github/workflows/bump.yml on every release
# of the CLI — do not edit them by hand.
class ImmichExport < Formula
  include Language::Python::Virtualenv

  desc "Export everything out of Immich into a plain, human-readable folder tree"
  homepage "https://github.com/fileworks/immich-export"
  url "https://files.pythonhosted.org/packages/2e/6e/f3d3ff9b92ecefe8dab872b9e712f06debcb033680497f7185d30b1182db/immich_export-0.0.3.tar.gz"
  sha256 "caa6d7b0f8e20f46f867f81faf8cba30c47d9c9b0d8fe4a8cba5e08b412de824"
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
