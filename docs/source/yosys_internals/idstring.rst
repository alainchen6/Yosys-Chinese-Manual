IdString
--------


设计
~~~~


字符串驻留是一种对内存中保存的字符串进行去重的做法。此时一个整数可以精确表示一
个唯一字符串。这还允许用整数比较代替字符串比较，从而更快。

出于性能、内存效率以及未来并行化的考虑，``IdString`` 是每个 ``Design`` 各自的
``TwinePool`` 中的索引，该池会对前缀去重。

最大的亮点在于，它允许你在现有 ``IdString`` 后追加后缀来构造新的 ``IdString``，
而无需复制其内容：

.. code-block:: cpp
   :caption: 后缀节点构造示例
   :name: idstring_suffix

   Wire *enable = module->addWire(TwineSpec::Suffix{cell->name, "_EN"}, 1);

``TwinePool`` 持有一块 ``TwineNode`` 数组，它继承由 ``std::deque`` 支撑的
``HashConsPool``，从而以空闲链表进行 bump 分配。
``HashConsPool`` 提供以内容哈希为索引的去重存储。
``IdString`` 作为驻留字符串，按底层字符串进行哈希。

``TwineSpec`` 建模未驻留的临时 twine 节点，``TwineNode`` 建模已驻留的节点。
于是 ``IdString`` 就是 ``TwinePool`` 内部 ``TwineNode`` 向量中的索引。
更具体地说，它是 32 位的，带偏移量，并带有公有性标记。
偏移量使它能够表示 ``kernel/constids.inc`` 中在编译期分配的标识符。
标记通过占用整数的最高位来实现“公有性”，过去这一点由首字符是 ``$`` 还是 ``\``
决定。
从设计源文件传入的用户指定名称是公有的，而 Yosys 创建的名称是私有的。

``TwineNode`` 使用 ``SmallString`` 将小字符串内联存储，较大的字符串则存于指针
之后。这使它自身的大小保持在 24 字节。
``AutoSuffix`` 是由 ``NEW_ID`` 和 ``NEW_ID_SUFFIX`` 宏产生的 ``TwineSpec`` 变
体。这些 ``TwineSpec`` 在重复驻留时会跳过对每个调用点固定前缀的字符串哈希。
``TwinePool`` 在驻留它们时会追加自己的 autoidx 计数器值，因此每个 ``Design``
独立地为其生成的名称编号。
整数后缀可以放入 ``SmallString`` 的内联存储。

垃圾回收会并行地追踪一个 ``Design``。

从全局驻留的 IdString 迁移
~~~~~~~~~~~~~~~~~~~~~~~~~~


C++ 核心改动
^^^^^^^^^^^^

``IdString`` <-> 字符串转换现在需要访问每个 ``Design`` 各自的 ``TwinePool``，可
以通过 ``design->twines()``、``module->twines()``、``wire->twines()``、
``cell->twines()``、``memory->twines()``、``process->twines()`` 访问

.. code-block:: diff

   -IdString id = "hello";
   +IdString id = design->twines().add("\\hello");

.. code-block:: diff

   -void thing(IdString id) {
   -    std::string s = id;
   -    log("%s\n", id);
   +void thing(Design* design, IdString id) {
   +    std::string s = design->twines().str(id);
   +    log("%s\n", s);
   // ...
   }

C++ 辅助工具
^^^^^^^^^^^^

当需要在传递一个 IdString 之后再把它转成字符串/打印，或从字符串赋值时，可以使用
``PooledName``，它实际上就是这个东西，但带有许多便捷方法：

.. code-block:: cpp

   class PooledName { const TwinePool *pool_; IdString id_; }

这样你就可以

.. code-block:: diff

   -void foo(IdString name) {
   +void foo(PooledName name) {
       log("%s\n", name);
   }

   for (IdString name : names)
   -    foo(name);
   +    foo({design, name});

   // This then works without a change, since Cell::name
   // can magically convert to PooledName
   for (Cell* cell : cells)
       foo(cell->name);

在 RTLIL 对象的 ``name`` 字段以及 ``Cell::type`` 中，``Design*`` 在上下文里是
可用的，因此这些字段会“魔法般地”包装一个 IdString 以供读取访问。这意味着这里
不需要改动：

.. code-block:: cpp

   log("Cell type %s, cell name %s\n", cell->type, cell->name);

但写访问则不行，所以仍然需要这样做：

.. code-block:: diff

   -cell->type = "\\asdfghjk";
   +cell->type = design->twines().add("\\asdfghjk");

现在检查 ``IdString`` 的首字符来判断公有性可能代价很高。请改为这样做：

.. code-block:: diff

   -if (wire->name[0] == '$')
   +if (!wire->name.isPublic())

``ID(id)`` 现在只接受 ``kernel/constids.inc`` 中的名称

.. code-block:: diff

   -auto w = miter_module->addWire(ID(asdfghjk));
   +auto w = miter_module->addWire("\\asdfghjk");

``IdString`` 仅在其所属的 ``Design`` 中有效：跨设计使用需要
``TwinePool::copy_from``、``TwinePool::find_from``、``Module::clone(Design *)``、
``RTLIL::copy_attr_dict``

``RTLIL::sort_by_id_str`` 接受一个 ``TwinePool`` 引用。现在正好可以重新考虑：
你是否真的想按字符串内容来排序！

.. code-block:: diff

   -modules_.sort(sort_by_id_str());
   +modules_.sort(sort_by_id_str(design->twines()));

``NEW_ID``、``NEW_ID_SUFFIX(suffix)`` 的类型从 ``IdString`` 变为 ``TwineSpec``。

但只要在构造 RTLIL 对象时使用它们，魔法就会发生：

.. code-block:: cpp

   SigSpec s = module->And(NEW_ID, lhs, rhs);

``RTLIL::unescape_id(IdString)`` 和 ``log_id`` 已被移除，其他依赖旧设计的设施也
一并移除。

如果在处理多个 ``Design`` 时遇到 bug，可以用
``YOSYS_ENABLE_TWINE_PROVENANCE`` CMake 变量启用额外检查。

在不同 ``Design`` 的对象之间复制属性字典和参数字典时，需要通过
``copy_attr_dict`` 来安全地重新驻留 twine。

Python 辅助工具
^^^^^^^^^^^^^^^

``pyosys`` 对你撒了个谎 —— 在 Python 中得到 ``IdString`` 时，你实际拿到的是
``PooledName``。这是因为我们期望 Python 用户在这里更看重便利和简单，而不是多
余的字节。这与我们 C++ 核心优化 pass（处理流程）所需要的不同。

字符串仍然可以作为 ``Design``、``Module``、``Cell``、``Wire``、``Memory`` 和
``Process`` 方法中的名称使用，也可以作为它们的 ``attributes``、``parameters``、
``parameter_default_values``、``connections_``、``wires_``、``cells_``、
``memories``、``processes`` 和 ``modules_`` 的键，因为这些对象知道自己的设计。

在其他地方，只有静态名称（``"\\A"``、``"$add"``）会从字符串转换。否则你可能需要
从设计中获取 ``IdString``：

.. code-block:: diff

   my_idict = ys.IdstringIdict()
   -my_idict("\\hello")
   -print(my_idict[0])
   +my_idict(design.id_add("\\hello"))
   +print(design.str(my_idict[0]))

如果只想查找名称而不添加，请使用 ``id_find`` 而不是 ``id_add``；名称不存在时它
返回 ``None``：

.. code-block:: diff

   -sel.selected_module("\\top")
   +sel.selected_module(design.id_find("\\top"))

``connections_``、``wires_``、``cells_``、``memories``、``processes`` 和
``modules_`` 不能再整体赋值，请改用方法：

.. code-block:: diff

   -cell.connections_ = {"\\A": sig}
   +cell.setPort("\\A", sig)

在设计被删除后使用其名称现在会抛出 ``RuntimeError``，所以如果你需要，请在设计
仍然存活时用 ``str()`` 转换它。

RTLIL
^^^^^

RTLIL 文本格式中新增了 ``metadata`` 段，其中包含 ``twines`` 段。较旧的 RTLIL
版本仍然可以读入，但较旧的 Yosys 版本无法读取这种格式。

要写出与旧版 Yosys 兼容的 RTLIL 格式，请使用 ``write_rtlil -readable``。它只会
丢弃前缀节点结构，不会丢弃字符串内容。要删除人类可读的注释以减小文件大小，请使
用 ``write_rtlil -small``。
