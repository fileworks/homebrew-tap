# NOTE: url/sha256/version pin are placeholders until the first PyPI release;
# .github/workflows/bump.yml rewrites them on every release of the CLI.
class ImmichExport < Formula
  include Language::Python::Virtualenv

  desc "Export everything out of Immich into a plain, human-readable folder tree"
  homepage "https://github.com/fileworks/immich-export"
  url "https://files.pythonhosted.org/packages/00/ec/d8a66b58f5bb5c532c38d0594bbc21b87aa10399d58e76b466b299d1f715/immich_export-0.0.2.tar.gz"
  sha256 "42970f4d13bd0e3f07d5f6cf776454eac019b157e90dcc0cd923d71ebe741ed5"
  license "MIT"

  depends_on "python@3.12"

  def install
    venv = virtualenv_create(libexec, "python3.12")
    # Personal-tap pattern: pip-install the pinned release with its deps
    # instead of vendoring every dependency as a resource block.
    system libexec/"bin/pip", "install", "--no-cache-dir", "immich-export==#{version}"
    bin.install_symlink libexec/"bin/immich-export"
  end

  test do
    assert_match "immich-export", shell_output("#{bin}/immich-export --version")
  end
end
