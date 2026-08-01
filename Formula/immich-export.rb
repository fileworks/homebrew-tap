# This file is generated atomically by .github/scripts/bump_formula.py.
# Runtime lock: https://raw.githubusercontent.com/fileworks/immich-export/82a0ec57d480d67b034360e9316ae3369df7e59e/uv.lock
# Runtime lock SHA-256: 664b5a9026454f33fe83259b786c0f63bc8aedda9a830077e7900a2e7651eff5
class ImmichExport < Formula
  include Language::Python::Virtualenv

  desc "Export Immich into a plain, human-readable folder tree"
  homepage "https://github.com/fileworks/immich-export"
  url "https://files.pythonhosted.org/packages/f5/28/82e6084e8504363c75e6d4bfe55397e90ef37377c3511948ebfc94c96bfe/immich_export-0.2.0.tar.gz"
  sha256 "68feafd6decbd320b530aea4978bcc2177561af2e18055a3a5efdb9da4cfb00a"
  license "MIT"

  depends_on "hatch" => :build
  depends_on "python@3.12"

  on_macos do
    on_arm do
      resource "pydantic-core" do
        url "https://files.pythonhosted.org/packages/19/95/6195171e385007300f0f5574592e467c568becce2d937a0b6804f218bc49/pydantic_core-2.46.4-cp312-cp312-macosx_11_0_arm64.whl"
        sha256 "962ccbab7b642487b1d8b7df90ef677e03134cf1fd8880bf698649b22a69371f"
      end
    end
    on_intel do
      resource "pydantic-core" do
        url "https://files.pythonhosted.org/packages/ce/8c/af022f0af448d7747c5154288d46b5f2bc5f17366eaa0e23e9aa04d59f3b/pydantic_core-2.46.4-cp312-cp312-macosx_10_12_x86_64.whl"
        sha256 "3245406455a5d98187ec35530fd772b1d799b26667980872c8d4614991e2c4a2"
      end
    end
  end

  on_linux do
    on_arm do
      resource "pydantic-core" do
        url "https://files.pythonhosted.org/packages/8e/bc/f47d1ff9cbb1620e1b5b697eef06010035735f07820180e74178226b27b3/pydantic_core-2.46.4-cp312-cp312-manylinux_2_17_aarch64.manylinux2014_aarch64.whl"
        sha256 "8233f2947cf85404441fd7e0085f53b10c93e0ee78611099b5c7237e36aacbf7"
      end
    end
    on_intel do
      resource "pydantic-core" do
        url "https://files.pythonhosted.org/packages/5f/97/2aab507d3d00ca626e8e57c1eac6a79e4e5fbcc63eb99733ff55d1717f65/pydantic_core-2.46.4-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
        sha256 "926c9541b14b12b1681dca8a0b75feb510b06c6341b70a8e500c2fdcff837cce"
      end
    end
  end

  resource "annotated-doc" do
    url "https://files.pythonhosted.org/packages/1e/d3/26bf1008eb3d2daa8ef4cacc7f3bfdc11818d111f7e2d0201bc6e3b49d45/annotated_doc-0.0.4-py3-none-any.whl"
    sha256 "571ac1dc6991c450b25a9c2d84a3705e2ae7a53467b5d111c24fa8baabbed320"
  end

  resource "annotated-types" do
    url "https://files.pythonhosted.org/packages/78/b6/6307fbef88d9b5ee7421e68d78a9f162e0da4900bc5f5793f6d3d0e34fb8/annotated_types-0.7.0-py3-none-any.whl"
    sha256 "1f02e8b43a8fbbc3f3e0d4f0f4bfc8131bcb4eebe8849b8e5c773f3a1c582a53"
  end

  resource "anyio" do
    url "https://files.pythonhosted.org/packages/b0/7b/90df4a0a816d98d6ea26f559d87836d494a2cf1fcf063be67df50a7bcc30/anyio-4.14.1-py3-none-any.whl"
    sha256 "4e5533c5b8ff0a24f5d7a176cbe6877129cd183893f66b537f8f227d10527d72"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/ef/2f/c5464532e965badff2f4c4c1a3a83f5697f0d7c407ed0cda44aaa99bb451/certifi-2026.6.17-py3-none-any.whl"
    sha256 "2227dcbaafe0d2f59279d1762ddddc37783ed4354594f194ffc31d20f41fc3db"
  end

  resource "h11" do
    url "https://files.pythonhosted.org/packages/04/4b/29cac41a4d98d144bf5f6d33995617b185d14b22401f75ca86f384e87ff1/h11-0.16.0-py3-none-any.whl"
    sha256 "63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86"
  end

  resource "httpcore" do
    url "https://files.pythonhosted.org/packages/7e/f5/f66802a942d491edb555dd61e3a9961140fd64c90bce1eafd741609d334d/httpcore-1.0.9-py3-none-any.whl"
    sha256 "2d400746a40668fc9dec9810239072b40b4484b640a8c38fd654a024c7a1bf55"
  end

  resource "httpx" do
    url "https://files.pythonhosted.org/packages/2a/39/e50c7c3a983047577ee07d2a9e53faf5a69493943ec3f6a384bdc792deb2/httpx-0.28.1-py3-none-any.whl"
    sha256 "d909fcccc110f8c7faf814ca82a9a4d816bc5a6dbfea25d6591d6985b8ba59ad"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/1e/5e/d4e9f1a599fb8e573b7b87160658329fbf28d19eac2718f51fc3def3aa5a/idna-3.18-py3-none-any.whl"
    sha256 "7f952cbe720b688055e3f87de14f5c3e5fdaa8bc3928985c4077ca689de849a2"
  end

  resource "markdown-it-py" do
    url "https://files.pythonhosted.org/packages/b3/81/4da04ced5a082363ecfa159c010d200ecbd959ae410c10c0264a38cac0f5/markdown_it_py-4.2.0-py3-none-any.whl"
    sha256 "9f7ebbcd14fe59494226453aed97c1070d83f8d24b6fc3a3bcf9a38092641c4a"
  end

  resource "mdurl" do
    url "https://files.pythonhosted.org/packages/b3/38/89ba8ad64ae25be8de66a6d463314cf1eb366222074cfda9ee839c56a4b4/mdurl-0.1.2-py3-none-any.whl"
    sha256 "84008a41e51615a49fc9966191ff91509e3c40b939176e643fd50a5c2196b8f8"
  end

  resource "pydantic" do
    url "https://files.pythonhosted.org/packages/fd/7b/122376b1fd3c62c1ed9dc80c931ace4844b3c55407b6fb2d199377c9736f/pydantic-2.13.4-py3-none-any.whl"
    sha256 "45a282cde31d808236fd7ea9d919b128653c8b38b393d1c4ab335c62924d9aba"
  end

  resource "pygments" do
    url "https://files.pythonhosted.org/packages/f4/7e/a72dd26f3b0f4f2bf1dd8923c85f7ceb43172af56d63c7383eb62b332364/pygments-2.20.0-py3-none-any.whl"
    sha256 "81a9e26dd42fd28a23a2d169d86d7ac03b46e2f8b59ed4698fb4785f946d0176"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/82/3b/64d4899d73f91ba49a8c18a8ff3f0ea8f1c1d75481760df8c68ef5235bf5/rich-15.0.0-py3-none-any.whl"
    sha256 "33bd4ef74232fb73fe9279a257718407f169c09b78a87ad3d296f548e27de0bb"
  end

  resource "shellingham" do
    url "https://files.pythonhosted.org/packages/e0/f9/0595336914c5619e5f28a1fb793285925a8cd4b432c9da0a987836c7f822/shellingham-1.5.4-py2.py3-none-any.whl"
    sha256 "7ecfff8f2fd72616f7481040475a65b2bf8af90a56c89140852d1120324e8686"
  end

  resource "typer" do
    url "https://files.pythonhosted.org/packages/80/87/b9fd69c92c6102a066e1b86a35243f53e70bd4c709f2a26d9f4fee4f4dc0/typer-0.26.8-py3-none-any.whl"
    sha256 "3512ca79ac5c11113414b36e80281b872884477722440691c89d1112e321a49c"
  end

  resource "typing-extensions" do
    url "https://files.pythonhosted.org/packages/49/d3/b8441a820a491ddfc024b0b0cf0393375b75ea13866d9c66727e54c2fc80/typing_extensions-4.16.0-py3-none-any.whl"
    sha256 "481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8"
  end

  resource "typing-inspection" do
    url "https://files.pythonhosted.org/packages/dc/9b/47798a6c91d8bdb567fe2698fe81e0c6b7cb7ef4d13da4114b41d239f65d/typing_inspection-0.4.2-py3-none-any.whl"
    sha256 "4ed1cacbdc298c220f1bd249ed5287caa16f34d44ef4e9c3d0cbad5b521545e7"
  end

  RUNTIME_INVENTORY = %w[
    immich-export annotated-doc annotated-types anyio certifi
    h11 httpcore httpx idna markdown-it-py
    mdurl pydantic pydantic-core pygments rich
    shellingham typer typing-extensions typing-inspection
  ].freeze

  def install
    ENV["PIP_NO_INDEX"] = "1"
    ENV["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    system formula_opt_libexec("hatch")/"bin/hatchling", "build", "-t", "wheel"

    wheelhouse = buildpath/"wheelhouse"
    wheelhouse.mkpath
    resources.each do |resource|
      wheelhouse.install resource.cached_download => resource.downloader.basename
    end

    venv = virtualenv_create(libexec, "python3.12")
    venv.pip_install Dir[wheelhouse/"*.whl"], build_isolation: false
    wheel = Dir["dist/*.whl"]
    odie "Expected exactly one application wheel" unless wheel.one?
    venv.pip_install_and_link wheel.first, build_isolation: false
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/immich-export --version")
    assert_match "Usage", shell_output("#{bin}/immich-export --help")
    script = <<~PYTHON
      import importlib.metadata
      import json
      import pathlib
      import sysconfig
      site = pathlib.Path(sysconfig.get_paths()["purelib"])
      names = sorted(
          distribution.metadata["Name"].lower().replace("_", "-")
          for distribution in importlib.metadata.distributions(path=[site])
      )
      print(json.dumps(names))
    PYTHON
    actual = JSON.parse(shell_output("#{libexec}/bin/python -c #{Shellwords.escape(script)}"))
    assert_equal RUNTIME_INVENTORY.sort, actual
  end
end
