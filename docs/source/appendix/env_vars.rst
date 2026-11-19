Yosys 环境变量
==============


``HOME``
   Yosys 的命令历史保存在 :file:`$HOME/.yosys_history`。图形输出（来自
   `show` 和 `viz` 命令）默认写入该目录。在某些情况下，该环境变量也用于
   解析带 :file:`~` 的文件名。

``PATH``
   在 OpenBSD 构建中，可能用于查找 Yosys 可执行文件的位置。

``TMPDIR``
   用于存放临时文件。

``ABC``
   当使用 :makevar:`YOSYS_ABC_EXECUTABLE` 以树外 ABC 编译 Yosys 时，该变量
   可用于覆盖外部的 ABC 可执行文件。

``YOSYS_NOVERIFIC``
   如果构建 Yosys 时启用了 Verific，该环境变量可用于临时禁用 Verific 支持。

``YOSYS_COVER_DIR`` 和 ``YOSYS_COVER_FILE``
   使用代码覆盖率时，这些环境变量控制输出文件的名称/位置。

``YOSYS_ABORT_ON_LOG_ERROR``
   可用于调试 Yosys 内部实现。将其设为 1 后，当 Yosys 因错误消息而终止时会
   调用 abort()。
