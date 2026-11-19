测试 Yosys
==========


.. todo:: 添加测试（makefile-tests 与 seed-tests）

运行自带的测试套件
------------------


Yosys 源码自带一个测试套件，用于防止回归并确保一切按预期工作。在 Yosys 根目录下
构建 ``test`` 目标即可运行测试。默认情况下，这会运行 vanilla 测试和单元测试。

.. code:: console

   cmake --preset default
   cmake --build build --target test --parallel $(nproc)

.. warning::

   使用 ``Ninja`` 作为生成器时存在一些限制，因此我们建议使用
   ``Unix Makefiles``，以便能够并行运行测试。不过，也可以直接运行：

.. code:: console

   cd tests
   make -j9

请注意，这种情况下默认的构建目录是 ``build``，但可以通过提供 :makevar:`BUILD_DIR`
变量来覆盖。

vanilla 测试
~~~~~~~~~~~~


.. TODO:: 针对测试基础设施的变更进行更新

这些测试构成了我们测试覆盖的大部分。它们可以用 ``test-vanilla`` CMake 目标运行。
通常它们的结构大致如下：你编写一个会被自动运行的 .ys 文件，该文件会用相对路径或
heredoc 运行 ``read_verilog`` 或 ``read_rtlil`` 这类前端，然后运行一些命令（其中
包括被测命令），接着用 :doc:`/using_yosys/more_scripting/selections` 配合
``-assert-count`` 进行检查。通常不需要在某个地方“注册”测试，只要把它添加到现有
目录中即可，具体取决于该目录里 ``run-test.sh`` 的工作方式。

单元测试
~~~~~~~~


运行单元测试需要以下额外软件包：

.. tab:: Ubuntu

   .. code:: console

      sudo apt-get install libgtest-dev

.. tab:: macOS

   无额外要求。

单元测试可以用 ``test-unit`` CMake 目标运行。

功能测试
~~~~~~~~


测试功能后端（参见
:doc:`/yosys_internals/extending_yosys/functional_ir`）除了
:ref:`getting_started/installation:构建前提条件` 中列出的要求之外，还有几项额外
要求：

.. tab:: Ubuntu

   .. code:: console

      sudo apt-get install racket
      raco pkg install rosette
      pip install pytest-xdist pytest-xdist-gnumake

.. tab:: macOS

   .. code:: console

      brew install racket
      raco pkg install rosette
      pip install pytest-xdist pytest-xdist-gnumake

如果你没有安装 :ref:`getting_started/installation:cad 套件` 中的任何一个，还应当
`按照他们的说明 <https://github.com/Z3Prover/z3>`_ 安装 Z3。

功能测试默认是禁用的，要启用它们，请使用下面的代码片段，然后照常运行测试：

.. code:: console

   cmake -B build . -DYOSYS_ENABLE_FUNCTIONAL_TESTS=ON
   cmake --build build --target test --parallel $(nproc)

或者只运行功能测试：

.. code:: console

   cmake --build build --target test-functional

文档测试
~~~~~~~~


还有一些额外的测试用于检查文档中包含的示例，可以用 ``test-docs`` CMake 目标
运行。这些测试还包括检查一些宏命令，以确保对它们的描述保持最新，主要面向 CI。


自动测试
--------


`Yosys Git repo`_ 在 Ubuntu 和 macOS 上，以及在一系列编译器版本上，都会自动
测试构建并运行自带的测试套件。有关最新信息（包括操作系统版本），请参阅
`the git actions page`_。

.. _Yosys Git repo: https://github.com/YosysHQ/yosys
.. _the git actions page: https://github.com/YosysHQ/yosys/actions

..
   How to add a unit test


   Unit test brings some advantages, briefly, we can list some of them (reference
   [1](https://en.wikipedia.org/wiki/Unit_testing)):

   * Tests reduce bugs in new features;
   * Tests reduce bugs in existing features;
   * Tests are good documentation;
   * Tests reduce the cost of change;
   * Tests allow refactoring;

   With those advantages in mind, it was required to choose a framework which fits
   well with C/C++ code.  Hence, `google test`_ was chosen, because it is widely
   used and it is relatively easy learn.

   .. _google test: https://github.com/google/googletest

   Install and configure google test (manually)


   In this section, you will see a brief description of how to install google test.
   However, it is strongly recommended that you take a look to the official
   repository (https://github.com/google/googletest) and refers to that if you have
   any problem to install it. Follow the steps below:

   * Install: cmake and pthread
   * Clone google test project from: https://github.com/google/googletest and enter
   in the project directory
   * Inside project directory, type:

   .. code-block:: console

      cmake -DBUILD_SHARED_LIBS=ON .
      make

   * After compilation, copy all ``*.so`` inside directory ``googlemock`` and
   ``googlemock/gtest`` to ``/usr/lib/``
   * Done! Now you can compile your tests.

   If you have any problem, go to the official repository to find help.

   Ps.: Some distros already have googletest packed. If your distro supports it,
   you can use it instead of compile.

   Create a new unit test


   If you want to add new unit tests for Yosys, just follow the steps below:

   * Go to directory :file:`test/unit/`
   * In this directory you can find something similar Yosys's directory structure.
   To create your unit test file you have to follow this pattern:
   fileNameToImplementUnitTest + Test.cc. E.g.: if you want to implement the unit
   test for ``kernel/celledges.cc``, you will need to create a file like this:
   ``tests/unit/kernel/celledgesTest.cc``;
   * Implement your unit test
   * Add unit test to file list in `CMakeLists.txt`
   In case unit tests are added to new directory, note that you need also to
   create new `CmakeList.txt` file and add ``yosys_gtest(dir-name unit-test.cc)```

   Run unit tests


   To compile and run all unit tests, just go to yosys root directory and type:

   .. code-block:: console

      cmake --build build --target test-unit
