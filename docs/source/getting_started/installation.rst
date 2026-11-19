安装
----


本文档将指导你完成 Yosys 的安装过程。

CAD 套件
~~~~~~~~


Yosys 是 `Tabby CAD Suite
<https://www.yosyshq.com/tabby-cad-datasheet>`_ 和 `OSS CAD Suite
<https://github.com/YosysHQ/oss-cad-suite-build>`_ 的一部分！使用 Yosys 最简单
的方式是安装二进制软件套件，其中包含所有必需的依赖项和相关工具。

* 联系 `YosysHQ <https://www.yosyshq.com/contact>`_ 获取 `Tabby CAD Suite
  <https://www.yosyshq.com/tabby-cad-datasheet>`_ 评估许可证和下载链接
* 或者访问 https://github.com/YosysHQ/oss-cad-suite-build/releases 下载免费的
  OSS CAD Suite
* 按照 `GitHub 上的安装说明
  <https://github.com/YosysHQ/oss-cad-suite-build#installation>`_ 操作

如果你需要工业级 SystemVerilog 和 VHDL 解析器等功能，请务必获取 Tabby CAD
Suite 评估许可证！

有关 Tabby CAD Suite 与 OSS CAD Suite 区别的更多信息，请访问
https://www.yosyshq.com/tabby-cad-datasheet

许多 Linux 发行版也提供 Yosys 二进制包，其中一些的版本比其他发行版更新。请
查看你的包管理器！

目标架构
^^^^^^^^

`OSS CAD Suite`_ 为以下架构发布 `nightly builds`_：

- **linux-x64** - 大多数个人 Linux 计算机
- **darwin-x64** - 使用 Intel CPU 的 macOS 12 或更高版本
- **darwin-arm64** - 使用 M1/M2 CPU 的 macOS 12 或更高版本
- **windows-x64** - 面向 Windows 10 和 11
- **linux-arm64** - 树莓派（Raspberry Pi）等装有 64 位操作系统的设备

有关目标架构以及当前构建状态的更多信息，请查看 `OSS CAD Suite`_ 的 git 仓库。

.. _OSS CAD Suite: https://github.com/YosysHQ/oss-cad-suite-build
.. _nightly builds: https://github.com/YosysHQ/oss-cad-suite-build/releases/latest

从源码构建
~~~~~~~~~~


Yosys 的源文件可以从 `YosysHQ/Yosys git repository`_ 获取。`ABC`_ 以及其他一些
用到的库以 git 子模块的形式包含在其中。要同时克隆这些子模块，可执行：

.. code:: console

   git clone --recurse-submodules https://github.com/YosysHQ/yosys.git  # ..or..
   git clone https://github.com/YosysHQ/yosys.git
   cd yosys
   git submodule update --init --recursive

.. _YosysHQ/Yosys git repository: https://github.com/yosyshq/yosys/
.. _ABC: https://github.com/berkeley-abc/abc

.. note::

   从 Yosys v0.47 起，发布包中包含一个 ``yosys.tar.gz`` 文件，它把全部源代码和
   全部子模块打包到单个归档中。可以将其作为不依赖 :program:`git` 的替代方案。

支持的平台
^^^^^^^^^^

以下平台受到支持并会定期测试：

- Linux
- macOS

其他平台可能可用，但其说明可能不是最新的，也不会定期测试：

- FreeBSD
- WSL
- 使用（例如）Cygwin 的 Windows

构建前提条件
^^^^^^^^^^^^

需要支持 C++20 的 C++ 编译器，以及一些标准工具，例如 GNU Flex、GNU Bison
（>=3.8）、CMake（>=3.28）、Make（或其他 CMake 生成器，如 Ninja）和
Python（>=3.11）。还有一些附加工具：readline、libffi、Tcl 和 zlib，如果可用
就会被使用，但它们都是可选的。`show` 命令使用 Graphviz 和 Xdot 来显示原理图。

安装所有前提条件：

.. tab:: Ubuntu 22.04

   .. code:: console

      sudo apt-get install gawk git make python3 lld bison clang flex \
         libffi-dev libfl-dev libreadline-dev pkg-config tcl-dev zlib1g-dev \
         graphviz xdot
      sudo snap install cmake --classic

.. tab:: Ubuntu 24.04

   .. code:: console

      sudo apt-get install gawk git cmake make python3 lld bison clang flex \
         libffi-dev libfl-dev libreadline-dev pkg-config tcl-dev zlib1g-dev \
         graphviz xdot

.. tab:: macOS 13（使用 Homebrew）

   .. code:: console

      brew tap Homebrew/bundle && brew bundle

.. tab:: MacPorts

   .. code:: console

      sudo port install bison cmake flex readline gawk libffi graphviz \
         pkgconfig python311 zlib tcl

.. tab:: FreeBSD

   .. code:: console

      pkg install bison cmake-core flex readline gawk libffi graphviz \
         pkgconf python311 tcl-wrapper

.. tab:: Nix

   .. code:: console

      nix-shell

   进入一个包含所有前提条件的 shell，所用 nixpkgs 版本由 ``flake.lock`` 中
   固定的修订版本决定。若要让 direnv 自动加载它，请在 ``.envrc`` 中写入
   ``use nix``。``nix develop`` 会给出相同的 shell，但会先把源码树（包括所有
   子模块）复制到 Nix store 中。

.. tab:: Cygwin

   使用以下命令安装所有前提条件，或选择这些附加包：

   .. code:: console

      setup-x86_64.exe -q --packages=bison,flex,gcc-core,gcc-g++,git,libffi-devel,libreadline-devel,cmake,make,pkg-config,python3,tcl-devel,zlib-devel

   .. warning::

      截至撰写本文时，Cygwin 最高仅支持 Python 3.9.16，而 Python 的最低要求
      版本是 3.11。这意味着 Cygwin 与许多基于 Python 的前端不兼容。虽然这
      目前不会阻止 Yosys 本身工作，但不保证会继续支持。使用 gcc 时，你可能
      还需要指定 ``CXXSTD=gnu++20`` 来解决缺少 ``strdup`` 函数的问题。建议
      改用适用于 Linux 的 Windows 子系统（WSL），并按照 Ubuntu 的说明操作。

..
   tab:: MSYS2 (MINGW64)

   .. code:: console

      pacman -S bison flex mingw-w64-x86_64-gcc git libffi-devel libreadline-devel make pkg-config python3 tcl-devel zlib-devel

   我无法让它正常工作；它在 ld 阶段失败，看起来是数学库问题：
   ``multiple definition of `tanh'`` 和
   ``undefined reference to `__imp_acosh'``，另外 `aiger2` 中的 ``seekg``
   等也不可用。

   .. note::

      ``config-msys2-64`` 目标使用带 ``mingw-w64-x86_64-`` 前缀的编译器，
      以便编译出的 exe 文件无需 MSYS2 shell 即可运行。

构建配置
^^^^^^^^

Yosys 的构建通过 CMake 配置，并使用若干影响构建过程的变量。设置一次性变量时，
CMake 提供 ``-D <var>=<value>`` 命令行选项。例如，禁用 zlib 支持：

.. code:: console

   cmake -B build . -DYOSYS_WITHOUT_ZLIB=ON

.. warning::

   Yosys 不支持在源码树内构建。如果从根 ``yosys`` 目录调用 :program:`cmake`，
   则必须提供 ``-B`` 选项。

对于更持久的配置，我们建议在根 ``yosys`` 目录中创建并使用
``CMakeUserPresets.json`` 文件。下面是一个示例文件，其中有两个配置：一个在
调用 ``cmake --preset clang`` 时启用 ccache 并将默认编译器设为 clang；另一个
在调用 ``cmake --preset without_zlib`` 时禁用 zlib 支持。可以用它代替手动指定
``-DYOSYS_WITHOUT_ZLIB=ON``：

.. code-block:: json
   :caption: CMakeUserPresets.json

   {
      "version": 1,
      "configurePresets": [
         {
			"name": "clang",
			"inherits": "default",
			"generator": "Unix Makefiles",
			"cacheVariables": {
				"CMAKE_C_COMPILER": "clang",
				"CMAKE_CXX_COMPILER": "clang++",
				"YOSYS_COMPILER_LAUNCHER": "ccache"
			}
		},
		{
			"name": "without_zlib",
			"inherits": "clang",
			"cacheVariables": {
				"YOSYS_WITHOUT_ZLIB": "ON"
			}
		}
      ]
   }

生成之后，可以用 :program:`ccmake` 检查并修改可用的构建变量，或者打开生成的
``build/CMakeCache.txt`` 文件：

.. code:: console

   ccmake build              #..or..
   vi build/CMakeCache.txt

如果你的 PATH 中有 clang 以及（兼容版本的） ``ld.lld``，建议通过设置
``CMAKE_INTERPROCEDURAL_OPTIMIZATION=ON`` 启用 LTO，以利用 lld 加速增量构建。
在 macOS 上，LTO 要求使用 Homebrew 提供的 clang，而不是 Xcode 提供的 clang。
例如：

.. code:: console

   cmake -B build . -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON \
      -DCMAKE_C_COMPILER=$(brew --prefix)/opt/llvm/bin/clang \
      -DCMAKE_CXX_COMPILER=$(brew --prefix)/opt/llvm/bin/clang++

也可以用 preset 实现：

.. code:: console

   cmake --preset lto

默认情况下，构建（和安装）Yosys 时会一并构建（和安装） `ABC`_，其可执行文件名为
:program:`yosys-abc`。若要改用已有的 ABC 可执行文件，请将 CMake 变量
:makevar:`YOSYS_ABC_EXECUTABLE` 设置为指向所需的可执行文件。

运行构建系统
^^^^^^^^^^^^

要使用默认设置快速安装 Yosys，请在根 ``yosys`` 目录中执行以下命令：

.. code:: console

   cmake --preset release --fresh
   cmake --build build-rel --config Release --parallel $(nproc)
   sudo cmake --install build-rel --strip

要使用已有配置，请使用 ``--build`` 选项，例如：

.. code:: console

   cmake --preset default
   ccmake build              # modify configuration
   cmake --build build

.. seealso::

   编译完成后如何测试 Yosys，请参阅
   :doc:`/yosys_internals/extending_yosys/test_suites`。

源码树与构建系统
~~~~~~~~~~~~~~~~


Yosys 的源码树按以下顶层目录组织：

``backends/``
   该目录为每个后端模块包含一个子目录。

``cmake/``
   CMake 在生成构建系统期间使用的附加 ``.cmake`` 文件。

``docs/``
   包含本文档的源码，包括图片和示例代码。

``examples/``
   包含将 Yosys 与其他工具配合使用的示例代码，其中包括 Yosys Python API 的
   演示，以及面向 Intel、Anlogic 等各种工具链的综合示例。

``frontends/``
   该目录为每个前端模块包含一个子目录。

``kernel/``
   该目录包含 Yosys 的全部核心功能。其中包括用于操作 RTLIL 数据结构的函数和
   定义（:file:`rtlil.{h|cc}`）、``main()`` 函数（:file:`driver.cc`）、用于生成
   日志消息的内部框架（:file:`log.{h|cc}`）、用于注册和调用 pass 的内部框架
   （:file:`register.{h|cc}`）、一些实际上并不算 pass 的核心命令
   （:file:`select.cc`、:file:`show.cc` 等），以及几个其他小型工具库。

``libs/``
   随 Yosys 构建一起打包的库放在此文件夹中。参见
   :doc:`/appendix/auxlibs`。

``misc/``
   其他不属于任何类别的杂项。

``passes/``
   该目录为每个 pass 或每组 pass 包含一个子目录。例如，截至撰写本文时，
   :file:`passes/hierarchy/` 目录包含三个 pass 的代码：`hierarchy`、`submod`
   和 `uniquify`。

``pyosys/``
   包含构建 :doc:`Pyosys </using_yosys/pyosys>` 所需的脚本和包装。

``techlibs/``
   该目录包含内部单元库中各单元的仿真模型和标准实现。

``tests/``
   该目录包含 Yosys 使用的单元测试和回归测试套件。参见
   :doc:`/yosys_internals/extending_yosys/test_suites`。

.. TODO:: CMAKE_TODO

   - 每个 pass 对应 ``yosys_<pass|test_pass|frontend|backend>(<name>)``

      - 参见 :file:`cmake/YosysComponent.cmake`

   - 如果使用子文件夹，请用 ``add_subdirectory(<name>)`` 将其添加到父目录的
     ``CMakeLists.txt`` 中

   - 以前的做法：

   Yosys 内核会自动检测链接到 Yosys 的所有命令。因此无需将额外命令添加到某个
   中央命令列表中。

   学习如何编写 pass 时，适合阅读的示例源码起点是
   :file:`passes/opt/dff/opt_dff.cc` 和 :file:`passes/opt/opt_merge.cc`。

   使用 Qt Creator IDE 的用户可以用 make qtcreator 生成 Qt Creator 工程文件。
   使用 Eclipse IDE 的用户可以在 Eclipse 的 “New Project” 对话框中选择
   “Makefile Project with Existing Code” 工程类型（只有安装 CDT 插件后才可用）
   来创建 Eclipse 工程，以便为 Yosys 编写扩展，或只是浏览 Yosys 代码库。
