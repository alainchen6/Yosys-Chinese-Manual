Yosys 中的哈希与关联数据结构
----------------------------


基于哈希的容器类
~~~~~~~~~~~~~~~~


Yosys 使用 ``dict<K, T>`` 和 ``pool<T>`` 作为主要容器类。
``dict<K, T>`` 实质上是 ``std::unordered_map<K, T>`` 的替代品，
``pool<T>`` 是 ``std::unordered_set<T>`` 的替代品。
主要特点是：

* ``dict<K, T>`` 和 ``pool<T>`` 比 std 容器快约 2 倍
  （不过这一说法已有十多年未经核实）

* 对 ``dict<K, T>`` 或 ``pool<T>`` 中元素的引用会因插入和删除操作而失效
  （类似于 ``std::vector<T>`` 上的 ``push_back()``）。

* 某些迭代器会因 ``erase()`` 而失效。具体来说，尚未越过被删除元素的迭代器
  会失效。（``erase()`` 本身返回指向下一个元素的有效迭代器。）

* 没有迭代器会因 ``insert()`` 而失效。元素被插入到 ``begin()`` 处。也就是说，
  只有从 ``begin()`` 开始的新迭代器才能看到插入的元素。

* 方法 ``.count(key, iterator)`` 与 ``.count(key)`` 类似，但只考虑可以通过该
  迭代器到达的元素。

* 迭代器可以比较。``it1 < it2`` 意味着可以通过 ``t1`` 到达 ``t2`` 的位置，
  但反过来不行。

* 可以用方法 ``.sort()`` 对容器中的元素排序，容器会保持有序，直到添加或删除
  元素。

* ``dict<K, T>`` 和 ``pool<T>`` 在所有编译器、标准库和体系结构上都具有相同的
  迭代顺序。

除 ``dict<K, T>`` 和 ``pool<T>`` 之外，还有 ``idict<K>``，它创建从 ``K`` 到
递增整数的双射。例如：

::

   idict<string, 42> si;
   log("%d\n", si("hello"));      // will print 42
   log("%d\n", si("world"));      // will print 43
   log("%d\n", si.at("world"));   // will print 43
   log("%d\n", si.at("dummy"));   // will throw exception
   log("%s\n", si[42]));  // will print hello
   log("%s\n", si[43]));  // will print world
   log("%s\n", si[44]));  // will throw exception

不能从 idict 中删除元素。

最后，``mfp<K>`` 在类型 ``K`` 上实现合并-查找集合数据结构（又称不相交集或
并查集）（“mfp” = merge-find-promote）。

哈希函数
~~~~~~~~


Yosys 中通常使用的哈希函数是 DJB2 的 XOR 版本：

::

   state = ((state << 5) + state) ^ value

这是一种为哈希 ASCII 字符而设计的经典哈希。Yosys 并不对大量 ASCII 文本做
哈希，但由于后文所述的因素，它恰好仍是一个局部最优解。

哈希函数的质量体现在多个方面，并且高度依赖于被哈希的内容。Yosys 不关心任何
密码学性质，其目标是在 Yosys 内部的数据模式下最小化总的哈希冲突风险。一般
来说，一个好的哈希函数会用计算快速且具有某些有益性质的数学函数把值折叠进
状态累加器。其中之一是雪崩效应，它要求输入中翻转一个位或加一这样的微小变化
在输出中产生巨大且不可预测的变化。此外，位独立性准则指出，当任意单个输入位
被反转时，任意一对输出位都应当独立变化。这些性质对于避免如下数据模式上的
哈希冲突很重要：使一个序列的哈希不与它的排列冲突，不在状态中丢失哈希先前
元素所添加的信息，等等。

DJB2 缺少这些性质。相反，由于 Yosys 要对大量由递增整数 ID 构成的数据结构
做哈希，Yosys 利用 DJB2 的可预测性来获得更低的哈希冲突，哈希的规律性在通过
与关联数据结构中“模素数”运算的交互后得以保留。例如，Yosys 中一些最常见的
对象是递增索引的内部化 ``IdString``\ s，或者典型情况下是带信号线内位偏移的
``SigBit``\ s（信号线由其唯一的 ``IdString`` 名字表示）。这正是 DJB2 成为
局部最优解的原因。此外，对某些类型，为此改用了 DJB2 的 ADD 版本（与上面相同，
但用加法代替 XOR），放弃了把值折叠进状态值的一般模式。

使类型可哈希
~~~~~~~~~~~~


我们先简化地看一下外部接口。一般来说，要得到 ``T obj`` 的哈希，你会调用工具
函数 ``run_hash<T>(const T& obj)``，它对应 ``hash_ops<T>::hash(obj)``，其默认
实现使用 ``hash_ops<T>::hash_into(Hasher(), obj)``。``Hasher`` 是实际实现哈希
函数的类，它隐藏其已初始化的内部状态，并在 ``hash_t yield()`` 时把该状态输出
（可能经过一些收尾步骤）。

``hash_ops<T>`` 是这里的主角。默认情况下，它通过
``Hasher T::hash_into(Hasher h)`` 方法传入 ``Hasher h``。要让一个记录（类或
结构体）类型能方便地用 Yosys hashlib 关联数据结构做哈希，你就必须实现这个
方法。

``hash_ops<T>`` 为 ``int`` 或 ``bool`` 等内建类型做了特化，并把指针与整数
同样对待，因此它不会解引用指针。由于许多 RTLIL 数据结构（如
``RTLIL::Wire``）带有自己的唯一索引 ``Hasher::hash_t hashidx_;``，在
``kernel/hashlib.h`` 中有针对 ``hash_ops<Wire*>`` 等的特化，它们会真正解引用
指针，并对所指向的实例调用 ``hash_into``。该索引来自对象所属
``RTLIL::Design`` 拥有的一个计数器，因此哈希以及 hashlib 容器中 RTLIL 对象的
迭代顺序只依赖于该设计的历史。``design -reset`` 会重启该计数器。

``hash_ops<T>`` 也为 ``std::pair<U>`` 等简单复合类型做了特化，依次对其成员
调用 hash_into。对于 ``std::vector<U>`` 等可变大小容器，会先对容器大小做哈希。
为自定义记录数据类型实现哈希也应当如此——除非有充分理由另作处理，否则对收到
的 ``Hasher h`` 依次对每个成员调用 ``h.eat(m)``，然后 ``return h;``。

在实现记录或其他复合类型的哈希时，不应当调用
``hash_ops<T>::hash(obj)`` 方法。编写它时，应按下文所示把它连接到
``hash_ops<T>::hash_into(Hasher h)``。如果你有充分理由并且必须为顶层哈希创建
特殊实现，请看看 ``kernel/rtlil.h`` 中
``hash_ops<RTLIL::SigBit>::hash(...)`` 是如何实现的。

从旧接口移植插件
~~~~~~~~~~~~~~~~


以前，在自定义类型上实现哈希的接口只是
``unsigned int T::hash() const``。这意味着成员的哈希是独立计算的，然后与哈希
函数临时组合起来，并掺入一些 xorshift 操作把位混合在一起。插件可以根据
``YS_HASHING_VERSION`` 是否存在及其取值同时实现两个接口，从而兼容破坏性变更
前后的两个版本。

.. code-block:: cpp
   :caption: 哈希兼容包装示例
   :name: hash_plugin_compat

   #ifndef YS_HASHING_VERSION
   unsigned int T::hash() const {
      return mkhash(a, b);
   }
   #elif YS_HASHING_VERSION == 1
   Hasher T::hash_into(Hasher h) const {
      h.eat(a);
      h.eat(b);
      return h;
   }
   Hasher T::hash() const {
      Hasher h;
      h.eat(*this);
      return h;
   }
   #else
   #error "Unsupported hashing interface"
   #endif

欢迎就相关问题联系 Yosys 维护者。
