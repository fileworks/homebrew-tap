# This file is generated atomically by .github/scripts/bump_formula.py.
# Runtime lock: https://raw.githubusercontent.com/fileworks/unpacksort/69dda440ffc0b46c28ada88308c427229434ca40/uv.lock
# Runtime lock SHA-256: 74c8ded17398577760cbb9d8be84029f3810c80bbae8760f4c824213c176f1a3
class Unpacksort < Formula
  include Language::Python::Virtualenv

  desc "Safely unpack, deduplicate, classify, and sort nested archives"
  homepage "https://github.com/fileworks/unpacksort"
  url "https://files.pythonhosted.org/packages/cc/5c/7611eff3b540e4af546212c919825c1b84e6428255f3d84d1f8a8f151a2e/unpacksort-1.1.1.tar.gz"
  sha256 "9c416b38a5c7dc875c43c6282c505977af04b86f46b228e22095482a4f849734"
  license "MIT"

  depends_on "hatch" => :build
  depends_on "python@3.12"

  uses_from_macos "libxml2"
  uses_from_macos "libxslt"

  on_macos do
    on_arm do
      resource "backports-zstd" do
        url "https://files.pythonhosted.org/packages/0c/76/f7c02efde81ebb9993586f9e435d2fd1191a6f806f640e4eeb8d004493ed/backports_zstd-1.6.0-cp312-cp312-macosx_11_0_arm64.whl"
        sha256 "1d146926e997d2d3de8212bdcbf4985344a2622ca3bec458d8908000a84fd883"
      end

      resource "brotli" do
        url "https://files.pythonhosted.org/packages/11/ee/b0a11ab2315c69bb9b45a2aaed022499c9c24a205c3a49c3513b541a7967/brotli-1.2.0-cp312-cp312-macosx_10_13_universal2.whl"
        sha256 "35d382625778834a7f3061b15423919aa03e4f5da34ac8e02c074e4b75ab4f84"
      end

      resource "inflate64" do
        url "https://files.pythonhosted.org/packages/ed/33/5cfa7468960de1be0833e7e41adf5b7804a0aef2fb46f3679df3876bf3ab/inflate64-1.0.4-cp312-cp312-macosx_10_13_universal2.whl"
        sha256 "c8009e4a4918ee6c8cbc49e58fe159464895064cfdf0565fed3f49ca81e45272"
      end

      resource "lxml" do
        url "https://files.pythonhosted.org/packages/6a/6e/c4add832b6fc1e887125b96f880d7b9b70aae5248718e046b1704bcac4b9/lxml-6.1.1-cp312-cp312-macosx_10_13_universal2.whl"
        sha256 "104c09bda8d2a562824c0e319d0768ce26a779b7601e0931d33b09b53c392ef7"
      end

      resource "pikepdf" do
        url "https://files.pythonhosted.org/packages/8a/94/a30157ea052c9f8c8c5fee97dceba09f374dd564ed91fa8b8d9c48cfb622/pikepdf-10.10.0-cp312-cp312-macosx_14_0_arm64.whl"
        sha256 "ccfa2288bbc206bfe7197f8614ee20de902e511ff968da86bebf814280124156"
      end

      resource "pillow" do
        url "https://files.pythonhosted.org/packages/d8/66/9a386a92561f402389a4fc70c18838bf6d35eb5eb5c6850b4b2dc64f5048/pillow-12.3.0-cp312-cp312-macosx_11_0_arm64.whl"
        sha256 "ffd0c5368496f41b0944be820fcb7a838aa6e623d250b01acf2643939c3f99d7"
      end

      resource "psutil" do
        url "https://files.pythonhosted.org/packages/80/c4/f5af4c1ca8c1eeb2e92ccca14ce8effdeec651d5ab6053c589b074eda6e1/psutil-7.2.2-cp36-abi3-macosx_11_0_arm64.whl"
        sha256 "1a7b04c10f32cc88ab39cbf606e117fd74721c831c98a27dc04578deb0c16979"
      end

      resource "pybcj" do
        url "https://files.pythonhosted.org/packages/09/32/63b96b702fc4848834ce552302fbdccad92f67886eaf3fbbed530569f4a1/pybcj-1.0.8-cp312-cp312-macosx_10_13_universal2.whl"
        sha256 "748af4545040da68dfae8cdf9f902ac7c29f209aaf6450a970abe0302d1b0f58"
      end

      resource "pycryptodomex" do
        url "https://files.pythonhosted.org/packages/dd/9c/1a8f35daa39784ed8adf93a694e7e5dc15c23c741bbda06e1d45f8979e9e/pycryptodomex-3.23.0-cp37-abi3-macosx_10_9_universal2.whl"
        sha256 "06698f957fe1ab229a99ba2defeeae1c09af185baa909a31a5d1f9d42b1aaed6"
      end

      resource "pyppmd" do
        url "https://files.pythonhosted.org/packages/3e/89/696046e53c7aea98bb563aed3f15c3e2fa20c33e3d6c9de3c20992c586cc/pyppmd-1.3.1-cp312-cp312-macosx_10_13_universal2.whl"
        sha256 "3faa58ab2ebe3b13ec23b1904639d687fb727270d2962fd2d239ca00fd6eb865"
      end

      resource "zstandard" do
        url "https://files.pythonhosted.org/packages/aa/1c/d920d64b22f8dd028a8b90e2d756e431a5d86194caa78e3819c7bf53b4b3/zstandard-0.25.0-cp312-cp312-macosx_11_0_arm64.whl"
        sha256 "913cbd31a400febff93b564a23e17c3ed2d56c064006f54efec210d586171c00"
      end
    end
    on_intel do
      resource "backports-zstd" do
        url "https://files.pythonhosted.org/packages/1e/bb/009af3a9532d4cc66d5385391c512210fae32ab2442605f26aca1d8d2957/backports_zstd-1.6.0-cp312-cp312-macosx_10_13_x86_64.whl"
        sha256 "0466b14723f3b7697669c00ee66fe16e30e25636b286b0a923fa86fa3d8a753c"
      end

      resource "brotli" do
        url "https://files.pythonhosted.org/packages/11/ee/b0a11ab2315c69bb9b45a2aaed022499c9c24a205c3a49c3513b541a7967/brotli-1.2.0-cp312-cp312-macosx_10_13_universal2.whl"
        sha256 "35d382625778834a7f3061b15423919aa03e4f5da34ac8e02c074e4b75ab4f84"
      end

      resource "inflate64" do
        url "https://files.pythonhosted.org/packages/ed/33/5cfa7468960de1be0833e7e41adf5b7804a0aef2fb46f3679df3876bf3ab/inflate64-1.0.4-cp312-cp312-macosx_10_13_universal2.whl"
        sha256 "c8009e4a4918ee6c8cbc49e58fe159464895064cfdf0565fed3f49ca81e45272"
      end

      resource "lxml" do
        url "https://files.pythonhosted.org/packages/6a/6e/c4add832b6fc1e887125b96f880d7b9b70aae5248718e046b1704bcac4b9/lxml-6.1.1-cp312-cp312-macosx_10_13_universal2.whl"
        sha256 "104c09bda8d2a562824c0e319d0768ce26a779b7601e0931d33b09b53c392ef7"
      end

      resource "pikepdf" do
        url "https://files.pythonhosted.org/packages/bc/86/313554efb00675f6e9b75bf012368e7c114174680f1c13035eba6e4a75de/pikepdf-10.10.0-cp312-cp312-macosx_15_0_x86_64.whl"
        sha256 "19c14b76a240f3cd067abc77b62843268d56dce45b7787ea70fd8cceb11cc5dc"
      end

      resource "pillow" do
        url "https://files.pythonhosted.org/packages/37/bf/fb3ebff8ddcb76aac5a01389251bbbb9519922a9b520d8247c1ca864a25d/pillow-12.3.0-cp312-cp312-macosx_10_13_x86_64.whl"
        sha256 "ba09209fbe443b4acccebe845d8a138b89a8f4fbaeedd44953490b5315d5e965"
      end

      resource "psutil" do
        url "https://files.pythonhosted.org/packages/e7/36/5ee6e05c9bd427237b11b3937ad82bb8ad2752d72c6969314590dd0c2f6e/psutil-7.2.2-cp36-abi3-macosx_10_9_x86_64.whl"
        sha256 "ed0cace939114f62738d808fdcecd4c869222507e266e574799e9c0faa17d486"
      end

      resource "pybcj" do
        url "https://files.pythonhosted.org/packages/09/32/63b96b702fc4848834ce552302fbdccad92f67886eaf3fbbed530569f4a1/pybcj-1.0.8-cp312-cp312-macosx_10_13_universal2.whl"
        sha256 "748af4545040da68dfae8cdf9f902ac7c29f209aaf6450a970abe0302d1b0f58"
      end

      resource "pycryptodomex" do
        url "https://files.pythonhosted.org/packages/dd/9c/1a8f35daa39784ed8adf93a694e7e5dc15c23c741bbda06e1d45f8979e9e/pycryptodomex-3.23.0-cp37-abi3-macosx_10_9_universal2.whl"
        sha256 "06698f957fe1ab229a99ba2defeeae1c09af185baa909a31a5d1f9d42b1aaed6"
      end

      resource "pyppmd" do
        url "https://files.pythonhosted.org/packages/3e/89/696046e53c7aea98bb563aed3f15c3e2fa20c33e3d6c9de3c20992c586cc/pyppmd-1.3.1-cp312-cp312-macosx_10_13_universal2.whl"
        sha256 "3faa58ab2ebe3b13ec23b1904639d687fb727270d2962fd2d239ca00fd6eb865"
      end

      resource "zstandard" do
        url "https://files.pythonhosted.org/packages/82/fc/f26eb6ef91ae723a03e16eddb198abcfce2bc5a42e224d44cc8b6765e57e/zstandard-0.25.0-cp312-cp312-macosx_10_13_x86_64.whl"
        sha256 "7b3c3a3ab9daa3eed242d6ecceead93aebbb8f5f84318d82cee643e019c4b73b"
      end
    end
  end

  on_linux do
    on_arm do
      resource "backports-zstd" do
        url "https://files.pythonhosted.org/packages/03/95/7ed25c90369360f96f8bfa961540845e063377c32a43b775201af66a588c/backports_zstd-1.6.0-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl"
        sha256 "7c2b1f4a640c51130caa92cef5bf72bd3c3dbbcfbf814c37403aa0601b1811b0"
      end

      resource "brotli" do
        url "https://files.pythonhosted.org/packages/3d/6f/feba03130d5fceadfa3a1bb102cb14650798c848b1df2a808356f939bb16/brotli-1.2.0-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl"
        sha256 "acec55bb7c90f1dfc476126f9711a8e81c9af7fb617409a9ee2953115343f08d"
      end

      resource "inflate64" do
        url "https://files.pythonhosted.org/packages/7f/66/c0c3d3b4b863aab2c2ce631d219a8eb3b95b78acd5f40d3212f071e693db/inflate64-1.0.4-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl"
        sha256 "6bfcf806912ced77a21394f7363805ecacd626b79f93cba87d505a48e88ede78"
      end

      resource "lxml" do
        url "https://files.pythonhosted.org/packages/42/95/bb63f0fd62e554fe078e1fb3c8fe9083c14ddc7ad7fa178d10e57e071ac7/lxml-6.1.1-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.whl"
        sha256 "c921ba5c51e4e9f63b8b00267d06566e1f63407408a0496da2d1d0bfc819c7fc"
      end

      resource "pikepdf" do
        url "https://files.pythonhosted.org/packages/a3/b6/0cceaa5a1084730154e8e948b181d2eee2f7f2f3a110b919263ea29e4a0a/pikepdf-10.10.0-cp312-cp312-manylinux_2_26_aarch64.manylinux_2_28_aarch64.whl"
        sha256 "81c938b33db9f32b7f419f06dbb97eca3e2629c57c0b18a7b719d81563c48d3f"
      end

      resource "pillow" do
        url "https://files.pythonhosted.org/packages/25/27/ac8f99618ffd3dde21db0f4d4b1d2ab00c0880595bfd17df103f7f39fd0c/pillow-12.3.0-cp312-cp312-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl"
        sha256 "d9c7f76c0673154f044e9d78c8655fb4213f6ca31a836df48b40fe5d187717b9"
      end

      resource "psutil" do
        url "https://files.pythonhosted.org/packages/63/65/37648c0c158dc222aba51c089eb3bdfa238e621674dc42d48706e639204f/psutil-7.2.2-cp36-abi3-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl"
        sha256 "b0726cecd84f9474419d67252add4ac0cd9811b04d61123054b9fb6f57df6e9e"
      end

      resource "pybcj" do
        url "https://files.pythonhosted.org/packages/05/0f/9db13432a6f8878f90c108a68fda46e832eea53585cb5dee8bdbc9472467/pybcj-1.0.8-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl"
        sha256 "b480efcd66cfb4533ede6c3d67224ff477c8dd661613826edff9c95921a562d6"
      end

      resource "pycryptodomex" do
        url "https://files.pythonhosted.org/packages/8c/fd/5a054543c8988d4ed7b612721d7e78a4b9bf36bc3c5ad45ef45c22d0060e/pycryptodomex-3.23.0-cp37-abi3-manylinux_2_17_aarch64.manylinux2014_aarch64.whl"
        sha256 "43c446e2ba8df8889e0e16f02211c25b4934898384c1ec1ec04d7889c0333587"
      end

      resource "pyppmd" do
        url "https://files.pythonhosted.org/packages/aa/9d/4a59b73ea8e305f9192ee26ceb7c3d57e17ccb9bcca0e99ef335db29fcf7/pyppmd-1.3.1-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl"
        sha256 "37b1883accf840cb0b711785d353f8548853a1401d381da007c0aec362f3ffac"
      end

      resource "zstandard" do
        url "https://files.pythonhosted.org/packages/1e/15/efef5a2f204a64bdb5571e6161d49f7ef0fffdbca953a615efbec045f60f/zstandard-0.25.0-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.whl"
        sha256 "6dffecc361d079bb48d7caef5d673c88c8988d3d33fb74ab95b7ee6da42652ea"
      end
    end
    on_intel do
      resource "backports-zstd" do
        url "https://files.pythonhosted.org/packages/6b/b2/d17b2722c636d64b4e77ddc68d8d0625719d39f94021be8719a218af4c0a/backports_zstd-1.6.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl"
        sha256 "1a99710fbb225d459d66def4dc2bb2cd4a9a0bdc8b799fc0621cfdd863be9c93"
      end

      resource "brotli" do
        url "https://files.pythonhosted.org/packages/03/a7/03aa61fbc3c5cbf99b44d158665f9b0dd3d8059be16c460208d9e385c837/brotli-1.2.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl"
        sha256 "072e7624b1fc4d601036ab3f4f27942ef772887e876beff0301d261210bca97f"
      end

      resource "inflate64" do
        url "https://files.pythonhosted.org/packages/37/00/1a2351a85d36b26c5b2b8cfbb37ad86084c98f592dd7590f8577d8b33993/inflate64-1.0.4-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl"
        sha256 "62d1aac3aba094ae42e27ce7581b414c90f218248be0953b6aeb11a127225e5d"
      end

      resource "lxml" do
        url "https://files.pythonhosted.org/packages/eb/99/0013e8d9b5960f4f041cf0b73e2f80c23eb5205b1f7bfb20203243651359/lxml-6.1.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl"
        sha256 "54a7f95e4de5fb94e2f9f4b9055c6ba33bf3d628fd77a1d647c5923caa2cdcdc"
      end

      resource "pikepdf" do
        url "https://files.pythonhosted.org/packages/46/b0/fc1e0e3f0a6a652f71387c4f9061457202369e98074def130f15173a7a6c/pikepdf-10.10.0-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl"
        sha256 "feccd53d5620c908fbb79399b2daee9103dee27d744bc80946daca22500be90f"
      end

      resource "pillow" do
        url "https://files.pythonhosted.org/packages/84/21/a35af28dcc61f37ed850a2d64c65c701321dfbf25085e469d5559360cbbf/pillow-12.3.0-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl"
        sha256 "78cb2c6865a35ab8ff8b75fd122f6033b92a62c82801110e48ddd6c936a45d91"
      end

      resource "psutil" do
        url "https://files.pythonhosted.org/packages/b5/70/5d8df3b09e25bce090399cf48e452d25c935ab72dad19406c77f4e828045/psutil-7.2.2-cp36-abi3-manylinux2010_x86_64.manylinux_2_12_x86_64.manylinux_2_28_x86_64.whl"
        sha256 "076a2d2f923fd4821644f5ba89f059523da90dc9014e85f8e45a5774ca5bc6f9"
      end

      resource "pybcj" do
        url "https://files.pythonhosted.org/packages/76/59/5629811698e6cfaea6cf159cf86fa471904ceb60448dc8b80233bba2e392/pybcj-1.0.8-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl"
        sha256 "a50b58f9b9d9978c55e3219b6816a1021a778b028a810b36aa754407591cb5ae"
      end

      resource "pycryptodomex" do
        url "https://files.pythonhosted.org/packages/c8/a9/8862616a85cf450d2822dbd4fff1fcaba90877907a6ff5bc2672cafe42f8/pycryptodomex-3.23.0-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
        sha256 "f489c4765093fb60e2edafdf223397bc716491b2b69fe74367b70d6999257a5c"
      end

      resource "pyppmd" do
        url "https://files.pythonhosted.org/packages/88/d7/fe32c2a4f8539365e6292aed25545830a5e718a510cdb4caddd6fd8d8056/pyppmd-1.3.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl"
        sha256 "1bd6d179ad39b6191ca0cbe62fb9592f33f49277b4384ad7bc5eb0e6ca27ebee"
      end

      resource "zstandard" do
        url "https://files.pythonhosted.org/packages/53/60/7be26e610767316c028a2cbedb9a3beabdbe33e2182c373f71a1c0b88f36/zstandard-0.25.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl"
        sha256 "5a56ba0db2d244117ed744dfa8f6f5b366e14148e00de44723413b2f3938a902"
      end
    end
  end

  resource "annotated-doc" do
    url "https://files.pythonhosted.org/packages/1e/d3/26bf1008eb3d2daa8ef4cacc7f3bfdc11818d111f7e2d0201bc6e3b49d45/annotated_doc-0.0.4-py3-none-any.whl"
    sha256 "571ac1dc6991c450b25a9c2d84a3705e2ae7a53467b5d111c24fa8baabbed320"
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/fb/e2/79c688af8b210d232694e31e59da9f6ec747bae31c3f5946e4e9b98860d5/click-8.4.2-py3-none-any.whl"
    sha256 "e6f9f66136c816745b9d65817da91d61d957fb16e02e4dcd0552553c5a197b76"
  end

  resource "markdown-it-py" do
    url "https://files.pythonhosted.org/packages/b3/81/4da04ced5a082363ecfa159c010d200ecbd959ae410c10c0264a38cac0f5/markdown_it_py-4.2.0-py3-none-any.whl"
    sha256 "9f7ebbcd14fe59494226453aed97c1070d83f8d24b6fc3a3bcf9a38092641c4a"
  end

  resource "mdurl" do
    url "https://files.pythonhosted.org/packages/b3/38/89ba8ad64ae25be8de66a6d463314cf1eb366222074cfda9ee839c56a4b4/mdurl-0.1.2-py3-none-any.whl"
    sha256 "84008a41e51615a49fc9966191ff91509e3c40b939176e643fd50a5c2196b8f8"
  end

  resource "multivolumefile" do
    url "https://files.pythonhosted.org/packages/22/31/ec5f46fd4c83185b806aa9c736e228cb780f13990a9cf4da0beb70025fcc/multivolumefile-0.2.3-py3-none-any.whl"
    sha256 "237f4353b60af1703087cf7725755a1f6fcaeeea48421e1896940cd1c920d678"
  end

  resource "packaging" do
    url "https://files.pythonhosted.org/packages/df/b2/87e62e8c3e2f4b32e5fe99e0b86d576da1312593b39f47d8ceef365e95ed/packaging-26.2-py3-none-any.whl"
    sha256 "5fc45236b9446107ff2415ce77c807cee2862cb6fac22b8a73826d0693b0980e"
  end

  resource "py7zr" do
    url "https://files.pythonhosted.org/packages/88/40/dc7f804abd0ea167ea8d4d9b3f5455321aaf671d040fcef647e9e952e714/py7zr-1.1.3-py3-none-any.whl"
    sha256 "17934a35089e026dec6c72ee275d9b841e646881ef822d618e805c3006661d9a"
  end

  resource "pygments" do
    url "https://files.pythonhosted.org/packages/f4/7e/a72dd26f3b0f4f2bf1dd8923c85f7ceb43172af56d63c7383eb62b332364/pygments-2.20.0-py3-none-any.whl"
    sha256 "81a9e26dd42fd28a23a2d169d86d7ac03b46e2f8b59ed4698fb4785f946d0176"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/b3/76/6d163cfac87b632216f71879e6b2cf17163f773ff59c00b5ff4900a80fa3/rich-14.3.4-py3-none-any.whl"
    sha256 "07e7adb4690f68864777b1450859253bed81a99a31ac321ac1817b2313558952"
  end

  resource "shellingham" do
    url "https://files.pythonhosted.org/packages/e0/f9/0595336914c5619e5f28a1fb793285925a8cd4b432c9da0a987836c7f822/shellingham-1.5.4-py2.py3-none-any.whl"
    sha256 "7ecfff8f2fd72616f7481040475a65b2bf8af90a56c89140852d1120324e8686"
  end

  resource "texttable" do
    url "https://files.pythonhosted.org/packages/24/99/4772b8e00a136f3e01236de33b0efda31ee7077203ba5967fcc76da94d65/texttable-1.7.0-py2.py3-none-any.whl"
    sha256 "72227d592c82b3d7f672731ae73e4d1f88cd8e2ef5b075a7a7f01a23a3743917"
  end

  resource "typer" do
    url "https://files.pythonhosted.org/packages/40/03/26a383c9e58c213199d1aad1c3d353cfc22d4444ec6d2c0bf8ad02523843/typer-0.27.0-py3-none-any.whl"
    sha256 "6f4b27631e47f077871b7dc30e933ec0131c1390fbe0e387ea5574b5bac9ccf1"
  end

  RUNTIME_INVENTORY = %w[
    unpacksort annotated-doc backports-zstd brotli click
    inflate64 lxml markdown-it-py mdurl multivolumefile
    packaging pikepdf pillow psutil py7zr
    pybcj pycryptodomex pygments pyppmd rich
    shellingham texttable typer zstandard
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
    assert_match version.to_s, shell_output("#{bin}/unpacksort --version")
    assert_match "Usage", shell_output("#{bin}/unpacksort --help")

    (testpath/"fixture").mkpath
    (testpath/"fixture/hello.txt").write("hello from the formula test\n")
    (testpath/"source").mkpath
    system "tar", "-czf", testpath/"source/fixture.tar.gz",
           "-C", testpath/"fixture", "hello.txt"
    system bin/"unpacksort", testpath/"source", testpath/"out"

    extracted = Dir.glob("#{testpath}/out/**/hello.txt").first
    refute_nil extracted, "unpacksort did not extract the fixture"
    assert_equal "hello from the formula test\n", File.read(extracted)
    manifest = testpath/"out/manifest.jsonl"
    assert_path_exists manifest
    assert_match "hello.txt", manifest.read

    script = <<~PYTHON
      import importlib.metadata
      import json
      import pathlib
      import sysconfig
      site = pathlib.Path(sysconfig.get_paths()["purelib"])
      names = sorted(
          distribution.metadata["Name"].lower().replace("_", "-").replace(".", "-")
          for distribution in importlib.metadata.distributions(path=[site])
      )
      print(json.dumps(names))
    PYTHON
    actual = JSON.parse(shell_output("#{libexec}/bin/python -c #{Shellwords.escape(script)}"))
    assert_equal RUNTIME_INVENTORY.sort, actual
  end
end
