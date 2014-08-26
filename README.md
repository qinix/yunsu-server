# 云速 server模块（已终止维护）

云速项目旨在提供最简单易用的翻墙服务，通过修改 shadowsocks 协议实现多用户、流量计算等功能。
云速项目开始于2013年7月，2013年11月因作者要专心准备高考，故宣布项目终止。云速项目于2014年
8月宣布开源，并搭建起一个 demo。demo 可以注册登录，但无法付款购买，可放心尝试。

云速项目分为两部分，第一部分为 web 模块，使用 Ruby + Sinatra，后端数据库使用 MongoDB + Redis
。另一部分为 server 模块，使用 Python 语言，拓展了 shadowsocks 协议与实现。demo 仅包括 web 部分。

Note：由于是本人早期项目，故代码质量一般，敬请谅解。

demo： <http://yunsu.qinixapp.com>

web模块源码：<http://github.com/qinix/yunsu-web>

server模块源码：<http://github.com/qinix/yunsu-server>

### LICENSE

The MIT License (MIT)

Copyright (c) 2014 Eric Zhang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

