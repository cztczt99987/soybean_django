const local: App.I18n.Schema = {
  system: {
    title: 'Soybean 管理系统',
    updateTitle: '系统版本更新通知',
    updateContent: '检测到系统有新版本发布，是否立即刷新页面？',
    updateConfirm: '立即刷新',
    updateCancel: '稍后再说'
  },
  common: {
    action: '操作',
    add: '新增',
    addSuccess: '添加成功',
    addChildMenu: '新增子菜单',
    addChildDept: '新增子部门',
    backToHome: '返回首页',
    batchDelete: '批量删除',
    cancel: '取消',
    close: '关闭',
    check: '勾选',
    selectAll: '全选',
    expandColumn: '展开列',
    columnSetting: '列设置',
    config: '配置',
    confirm: '确认',
    delete: '删除',
    deleteSuccess: '删除成功',
    confirmDelete: '确认删除吗？',
    edit: '编辑',
    warning: '警告',
    error: '错误',
    iconPicker: {
      title: '选择图标',
      search: '搜索图标',
      clear: '清空',
      categories: {
        common: '常用',
        system: '系统',
        user: '用户',
        file: '文件',
        edit: '编辑',
        chart: '图表',
        message: '通讯',
        navigate: '导航'
      }
    },
    index: '序号',
    keywordSearch: '请输入关键词搜索',
    logout: '退出登录',
    logoutConfirm: '确认退出登录吗？',
    lookForward: '敬请期待',
    modify: '修改',
    modifySuccess: '修改成功',
    noData: '无数据',
    operate: '操作',
    pleaseCheckValue: '请检查输入的值是否合法',
    refresh: '刷新',
    reset: '重置',
    search: '搜索',
    switch: '切换',
    tip: '提示',
    trigger: '触发',
    update: '更新',
    updateSuccess: '更新成功',
    userCenter: '个人中心',
    yesOrNo: {
      yes: '是',
      no: '否'
    }
  },
  request: {
    logout: '请求失败后登出用户',
    logoutMsg: '用户状态失效，请重新登录',
    logoutWithModal: '请求失败后弹出模态框再登出用户',
    logoutWithModalMsg: '用户状态失效，请重新登录',
    refreshToken: '请求的token已过期，刷新token',
    tokenExpired: 'token已过期'
  },
  theme: {
    themeDrawerTitle: '主题配置',
    tabs: {
      appearance: '外观',
      layout: '布局',
      general: '通用',
      preset: '预设'
    },
    appearance: {
      themeSchema: {
        title: '主题模式',
        light: '亮色模式',
        dark: '暗黑模式',
        auto: '跟随系统'
      },
      grayscale: '灰色模式',
      colourWeakness: '色弱模式',
      themeColor: {
        title: '主题颜色',
        primary: '主色',
        info: '信息色',
        success: '成功色',
        warning: '警告色',
        error: '错误色',
        followPrimary: '跟随主色'
      },
      themeRadius: {
        title: '主题圆角'
      },
      recommendColor: '应用推荐算法的颜色',
      recommendColorDesc: '推荐颜色的算法参照',
      preset: {
        title: '主题预设',
        apply: '应用',
        applySuccess: '预设应用成功',
        default: {
          name: '默认预设',
          desc: 'Soybean 默认主题预设'
        },
        dark: {
          name: '暗色预设',
          desc: '适用于夜间使用的暗色主题预设'
        },
        compact: {
          name: '紧凑型',
          desc: '适用于小屏幕的紧凑布局预设'
        },
        azir: {
          name: 'Azir的预设',
          desc: '是 Azir 比较喜欢的莫兰迪色系冷淡风'
        }
      }
    },
    layout: {
      layoutMode: {
        title: '布局模式',
        vertical: '左侧菜单模式',
        'vertical-mix': '左侧菜单混合模式',
        'vertical-hybrid-header-first': '左侧混合-顶部优先',
        horizontal: '顶部菜单模式',
        'top-hybrid-sidebar-first': '顶部混合-侧边优先',
        'top-hybrid-header-first': '顶部混合-顶部优先',
        vertical_detail: '左侧菜单布局，菜单在左，内容在右。',
        'vertical-mix_detail': '左侧双菜单布局，一级菜单在左侧深色区域，二级菜单在左侧浅色区域。',
        'vertical-hybrid-header-first_detail':
          '左侧混合布局，一级菜单在顶部，二级菜单在左侧深色区域，三级菜单在左侧浅色区域。',
        horizontal_detail: '顶部菜单布局，菜单在顶部，内容在下方。',
        'top-hybrid-sidebar-first_detail': '顶部混合布局，一级菜单在左侧，二级菜单在顶部。',
        'top-hybrid-header-first_detail': '顶部混合布局，一级菜单在顶部，二级菜单在左侧。'
      },
      tab: {
        title: '标签栏设置',
        visible: '显示标签栏',
        cache: '标签栏信息缓存',
        cacheTip: '离开页面后仍然保留标签栏信息',
        height: '标签栏高度',
        mode: {
          title: '标签栏风格',
          slider: '滑块风格',
          chrome: '谷歌风格',
          button: '按钮风格'
        },
        closeByMiddleClick: '鼠标中键关闭标签页',
        closeByMiddleClickTip: '启用后可以使用鼠标中键点击标签页进行关闭'
      },
      header: {
        title: '头部设置',
        height: '头部高度',
        breadcrumb: {
          visible: '显示面包屑',
          showIcon: '显示面包屑图标'
        }
      },
      sider: {
        title: '侧边栏设置',
        inverted: '深色侧边栏',
        width: '侧边栏宽度',
        collapsedWidth: '侧边栏折叠宽度',
        mixWidth: '混合布局侧边栏宽度',
        mixCollapsedWidth: '混合布局侧边栏折叠宽度',
        mixChildMenuWidth: '混合布局子菜单宽度',
        autoSelectFirstMenu: '自动选择第一个子菜单',
        autoSelectFirstMenuTip: '点击一级菜单时，自动选择并导航到第一个子菜单的最深层级'
      },
      footer: {
        title: '底部设置',
        visible: '显示底部',
        fixed: '固定底部',
        height: '底部高度',
        right: '底部居右'
      },
      content: {
        title: '内容区域设置',
        scrollMode: {
          title: '滚动模式',
          tip: '主题滚动仅 main 部分滚动，外层滚动可携带头部底部一起滚动',
          wrapper: '外层滚动',
          content: '主体滚动'
        },
        page: {
          animate: '页面切换动画',
          mode: {
            title: '页面切换动画类型',
            'fade-slide': '滑动',
            fade: '淡入淡出',
            'fade-bottom': '底部消退',
            'fade-scale': '缩放消退',
            'zoom-fade': '渐变',
            'zoom-out': '闪现',
            none: '无'
          }
        },
        fixedHeaderAndTab: '固定头部和标签栏'
      }
    },
    general: {
      title: '通用设置',
      watermark: {
        title: '水印设置',
        visible: '显示全屏水印',
        text: '自定义水印文本',
        enableUserName: '启用用户名水印',
        enableTime: '显示当前时间',
        timeFormat: '时间格式'
      },
      multilingual: {
        title: '多语言设置',
        visible: '显示多语言按钮'
      },
      globalSearch: {
        title: '全局搜索设置',
        visible: '显示全局搜索按钮'
      }
    },
    configOperation: {
      copyConfig: '复制配置',
      copySuccessMsg: '复制成功，请替换 src/theme/settings.ts 中的变量 themeSettings',
      resetConfig: '重置配置',
      resetSuccessMsg: '重置成功'
    }
  },
  route: {
    login: '登录',
    403: '无权限',
    404: '页面不存在',
    500: '服务器错误',
    'iframe-page': '外链页面',
    home: '首页',
    'system': '系统管理',
    'system_config': '参数设置',
    'system_dept': '部门管理',
    'system_dict': '字典管理',
    'system_log': '日志管理',
    'system_menu': '菜单管理',
    'system_post': '岗位管理',
    'system_role': '角色管理',
    'system_user': '用户管理',
    'monitor': '监控管理',
    'monitor_server': '服务器信息',
    'monitor_cache': '缓存监控',
    'monitor_file': '文件管理',
    'apis': '接口管理',
    'apis_docs': 'Swagger文档',
    'task': '任务管理',
    'task_job': '定时任务',
    'task_scheduler': '调度器监控',
    'task_node': '节点管理',
  },
  page: {
    task: {
      job: {
        title: '定时任务',
        name: '任务名称',
        namePlaceholder: '请输入任务名称',
        description: '任务描述',
        jobType: '任务类型',
        typeFunction: '内置函数',
        typeHttp: 'HTTP请求',
        handler: '内置处理器',
        httpMethod: '请求方法',
        httpUrl: '请求地址',
        httpBody: '请求体',
        triggerType: '触发方式',
        triggerCron: 'CRON表达式',
        triggerInterval: '固定间隔',
        triggerDate: '指定时间',
        cronExpr: 'CRON表达式',
        cronRule: '请填写 CRON 表达式',
        intervalSeconds: '间隔秒数',
        runDate: '执行时间',
        priority: '优先级',
        priorityHigh: '高',
        priorityMedium: '中',
        priorityLow: '低',
        timeout: '超时秒数',
        status: '任务状态',
        statusPlaceholder: '请选择状态',
        sortOrder: '排序',
        remark: '备注',
        nextRunAt: '下次执行时间',
        lastRunAt: '上次执行时间',
        runOnce: '测试',
        runOnceSent: '已触发执行，请稍后查看结果',
        pause: '暂停',
        pauseConfirm: '确认暂停该任务吗?',
        resume: '恢复',
        logs: '历史',
        logTitle: '执行历史',
        execStatus: '执行状态',
        startedAt: '开始时间',
        duration: '耗时',
        node: '执行节点',
        output: '执行输出',
        viewDetail: '查看'
      },
      scheduler: {
        state: '运行状态',
        stateRunning: '运行中',
        statePaused: '已暂停',
        stateStopped: '已停止',
        scheduler: '调度器',
        nodesOnline: '在线节点',
        tasks: '任务',
        start: '启动',
        pause: '暂停',
        resume: '恢复',
        shutdown: '关闭',
        shutdownConfirm: '确认关闭调度器吗? 关闭后所有任务停止调度',
        clearJobs: '清空任务',
        clearConfirm: '确认从调度器中移除全部任务吗?',
        console: '控制台',
        consoleTitle: '调度器控制台',
        consoleTip: '每 3 秒自动刷新',
        keyword: '关键字过滤',
        test: '测试',
        cardRunning: '运行中',
        cardPaused: '已暂停',
        noNextRun: '未排期',
        metricsTitle: '监控指标',
        uptime: '运行时长',
        mem: '内存占用',
        todayTotal: '今日执行',
        successRate: '成功率',
        avgDuration: '平均耗时',
        todayFailed: '今日失败',
        alerts: '异常报警',
        alertsEmpty: '暂无异常, 一切正常',
        recentLogs: '最近执行日志',
        alertBanner: '检测到 {count} 条异常报警, 请及时处理!',
        normalBanner: '调度器运行正常, 任务按计划调度执行中'
      },
      node: {
        title: '节点列表',
        name: '节点名称',
        nodeId: '节点标识',
        nodeIdTip: '节点唯一标识 (nodeId)',
        host: '主机地址',
        port: '端口',
        maxConcurrency: '最大并发',
        online: '在线',
        offline: '离线',
        disabled: '已禁用',
        local: '本机',
        load: '负载',
        heartbeatAt: '最后心跳',
        never: '从未上报',
        toggleEnable: '启用',
        toggleDisable: '禁用',
        totalNodes: '节点总数',
        onlineNodes: '在线节点',
        disabledNodes: '禁用节点',
        totalLoad: '总负载'
      }
    },
    login: {
      common: {
        loginOrRegister: '登录 / 注册',
        userNamePlaceholder: '请输入用户名',
        phonePlaceholder: '请输入手机号',
        codePlaceholder: '请输入验证码',
        captchaPlaceholder: '请输入计算结果',
        passwordPlaceholder: '请输入密码',
        confirmPasswordPlaceholder: '请再次输入密码',
        codeLogin: '验证码登录',
        confirm: '确定',
        back: '返回',
        validateSuccess: '验证成功',
        loginSuccess: '登录成功',
        welcomeBack: '欢迎回来，{userName} ！'
      },
      pwdLogin: {
        title: '密码登录',
        rememberMe: '记住我',
        forgetPassword: '忘记密码？',
        register: '注册账号',
        otherAccountLogin: '其他账号登录',
        otherLoginMode: '其他登录方式',
        superAdmin: '超级管理员',
        admin: '管理员',
        user: '普通用户'
      },
      codeLogin: {
        title: '验证码登录',
        getCode: '获取验证码',
        reGetCode: '{time}秒后重新获取',
        sendCodeSuccess: '验证码发送成功',
        imageCodePlaceholder: '请输入图片验证码'
      },
      register: {
        title: '注册账号',
        agreement: '我已经仔细阅读并接受',
        protocol: '《用户协议》',
        policy: '《隐私权政策》'
      },
      resetPwd: {
        title: '重置密码'
      },
      bindWeChat: {
        title: '绑定微信'
      }
    },
    home: {
      branchDesc:
        '为了方便大家开发和更新合并，我们对main分支的代码进行了精简，只保留了首页菜单，其余内容已移至example分支进行维护。预览地址显示的内容即为example分支的内容。',
      greeting: '早安，{userName}, 今天又是充满活力的一天!',
      weatherDesc: '今日多云转晴，20℃ - 25℃!',
      projectCount: '项目数',
      todo: '待办',
      message: '消息',
      downloadCount: '下载量',
      registerCount: '注册量',
      schedule: '作息安排',
      study: '学习',
      work: '工作',
      rest: '休息',
      entertainment: '娱乐',
      visitCount: '访问量',
      turnover: '成交额',
      dealCount: '成交量',
      projectNews: {
        title: '项目动态',
        moreNews: '更多动态',
        desc1: 'Soybean 在2021年5月28日创建了开源项目 soybean-admin!',
        desc2: 'Yanbowe 向 soybean-admin 提交了一个bug，多标签栏不会自适应。',
        desc3: 'Soybean 准备为 soybean-admin 的发布做充分的准备工作!',
        desc4: 'Soybean 正在忙于为soybean-admin写项目说明文档！',
        desc5: 'Soybean 刚才把工作台页面随便写了一些，凑合能看了！'
      },
      creativity: '创意'
    },
    system: {
      user: {
        title: '用户管理',
        form: { username: '登录账号', nickname: '用户昵称', password: '初始密码', email: '邮箱', phone: '手机号', gender: '性别', dept: '归属部门', roles: '角色', posts: '岗位', status: '状态', remark: '备注' },
        action: { resetPwd: '重置密码', changeStatus: '启用/停用' }
      },
      role: {
        title: '角色管理',
        form: { name: '角色名称', code: '角色编码', dataScope: '数据权限', menus: '菜单权限', departments: '数据权限部门', status: '状态', remark: '备注' },
        action: { assignMenus: '分配菜单', assignPermission: '权限分配' },
        assign: { dataAuth: '数据授权', dataAuthTip: '设置角色的数据可见范围', menuAuth: '菜单授权', menuAuthTip: '勾选角色可访问的菜单与按钮权限', searchMenu: '搜索菜单名称', expand: '展开', collapse: '收起', parentLinkage: '父子联动' }
      },
      menu: {
        title: '菜单管理',
        form: { parent: '上级菜单', name: '路由名', title: '显示名称', path: '路由路径', component: '组件路径', permission: '权限标识', icon: '图标', type: '类型', order: '排序', i18nKey: '国际化键', keepAlive: '缓存页面', hideInMenu: '隐藏菜单', externalLink: '外链', status: '状态', remark: '备注' }
      },
      dept: {
        title: '部门管理',
        form: { parent: '上级部门', name: '部门名称', code: '部门编码', leader: '负责人', phone: '联系电话', email: '邮箱', status: '状态', remark: '备注' }
      },
      post: {
        title: '岗位管理',
        form: { name: '岗位名称', code: '岗位编码', status: '状态', sortOrder: '排序', remark: '备注' }
      },
      dict: {
        title: '字典管理',
        typeTab: '字典类型',
        dataTab: '字典数据',
        selectTypePlaceholder: '请选择字典类型',
        selectTypeFirst: '请先选择字典类型',
        form: { name: '字典名称', code: '字典编码', status: '状态', remark: '备注' },
        data: { label: '标签', value: '键值', cssClass: '样式属性', listClass: '回显样式', isDefault: '是否默认', status: '状态', remark: '备注' }
      },
      config: {
        title: '参数设置',
        form: { name: '参数名称', code: '参数键名', value: '参数键值', valueType: '类型', isSystem: '系统内置', status: '状态', remark: '备注' }
      },
      log: {
        title: '日志管理',
        fields: { username: '账号', module: '模块', description: '描述', operationType: '操作类型', method: '方法', url: 'URL', ip: 'IP', status: '状态', costTime: '耗时', operatedAt: '操作时间', dateRange: '时间范围' },
        action: { clean: '清理N天前', cleanTitle: '清理日志', cleanDays: '清理多少天前的日志', day: '天' }
      },
      common: {
        createdAt: '创建时间',
        enabled: '正常',
        disabled: '停用',
        success: '成功',
        failure: '失败',
        gender: { unknown: '未知', male: '男', female: '女' },
        valueType: { S: '字符串', N: '数字', B: '布尔', J: 'JSON' },
        menuType: { dir: '目录', menu: '菜单', button: '按钮' },
        dataScope: { all: '全部数据权限', custom: '自定义数据权限', dept: '本部门数据权限', deptAndChildren: '本部门及以下数据权限', self: '仅本人数据权限' },
        operationType: { other: '其它', create: '新增', update: '修改', remove: '删除', grant: '授权', export: '导出', import: '导入', login: '登录', logout: '登出' },
        resetPwdSuccess: '密码重置成功',
        resetPwdConfirm: '确认重置该用户的密码吗？',
        changeStatusSuccess: '状态修改成功',
        assignMenusSuccess: '菜单分配成功',
        assignPermissionSuccess: '权限分配成功',
        cleanSuccess: '清理成功',
        dateRange: '时间范围'
      }
    },
    monitor: {
      server: {
        title: '服务器信息',
        refresh: '刷新',
        basic: '基本信息',
        os: '操作系统',
        hostname: '主机名',
        osName: '系统名称',
        osVersion: '系统版本',
        osRelease: '内核版本',
        arch: 'CPU 架构',
        cpuModel: 'CPU 型号',
        pythonVersion: 'Python 版本',
        djangoVersion: 'Django 版本',
        bootTime: '启动时间',
        uptime: '运行时长',
        cpu: 'CPU',
        physicalCores: '物理核心',
        logicalCores: '逻辑核心',
        usage: '使用率',
        freq: '主频(MHz)',
        memory: '内存',
        total: '总量',
        used: '已使用',
        available: '可用',
        usagePercent: '使用率',
        swapTotal: 'Swap 总量',
        swapUsed: 'Swap 已使用',
        swapUsage: 'Swap 使用率',
        disk: '磁盘',
        device: '设备',
        mountpoint: '挂载点',
        fstype: '文件系统',
        free: '剩余',
        network: '网络',
        ip: '本机 IP',
        bytesSent: '发送字节',
        bytesRecv: '接收字节',
        packetsSent: '发送包数',
        packetsRecv: '接收包数',
        process: '应用进程',
        pid: '进程号'
      },
      cache: {
        title: '缓存监控',
        notRedis: '当前未启用 Redis（内存缓存模式），暂不支持缓存管理',
        key: '键名',
        type: '类型',
        size: '大小',
        ttl: '过期时间',
        ttlNone: '永不过期',
        serverInfo: 'Redis 信息',
        redisVersion: 'Redis 版本',
        usedMemory: '已用内存',
        maxMemory: '最大内存',
        connectedClients: '连接数',
        dbSize: '键总数',
        deleteConfirm: '确认删除选中的缓存键吗？',
        allCategories: '全部分类',
        category: '分类',
        deleteCategory: '删除该分类',
        deleteCategoryConfirm: '确认删除该分类下的全部缓存键吗？相关缓存会在下次访问时自动重建。',
        cacheList: '缓存列表',
        keyList: '键名列表',
        cacheContent: '缓存内容',
        cacheName: '缓存名称',
        cacheKeyName: '缓存键名',
        remark: '备注',
        selectCategoryTip: '请先选择左侧缓存分类',
        selectKeyTip: '点击键名查看缓存内容',
        monitorInfoTab: '监控信息',
        cacheManageTab: '缓存管理',
        redisInfo: 'Redis监控信息',
        commandStats: '命令统计',
        memoryInfo: '内存信息',
        memoryUsage: '内存消耗',
        runMode: '运行模式',
        port: '端口',
        uptimeDays: '运行时间(天)',
        usedCpu: '使用CPU',
        memoryConfig: '内存配置',
        rdbStatus: 'RDB状态',
        netIo: '网络IO',
        aofOn: '开启',
        aofOff: '关闭',
        cleanAll: '清空全部',
        cleanAllConfirm: '确认清空当前库全部缓存吗？此操作不可恢复！',
        deleteSuccess: '删除成功',
        keywordPlaceholder: '请输入键名关键字'
      },
      file: {
        title: '文件管理',
        browser: '目录浏览',
        storage: '存储配置',
        name: '名称',
        size: '大小',
        modified: '修改时间',
        download: '下载',
        up: '返回上级',
        root: '根目录',
        emptyDir: '空目录',
        activeStorage: '当前激活',
        currentActive: '当前使用的存储方式',
        switchTo: '切换为此存储',
        switchConfirm: '确认切换存储方式吗？切换后新上传文件将使用所选存储',
        switchSuccess: '切换成功',
        save: '保存配置',
        validate: '验证配置',
        saveSuccess: '保存成功',
        validateSuccess: '配置验证通过',
        typeLocal: '本地存储',
        typeAliyun: '阿里云 OSS',
        typeTencent: '腾讯云 COS',
        typeQiniu: '七牛云 Kodo',
        fields: {
          basePath: '本地根目录',
          endpoint: '接入点 Endpoint',
          bucket: '存储空间 Bucket',
          accessKeyId: 'AccessKeyId',
          accessKeySecret: 'AccessKeySecret',
          region: '地域 Region',
          secretId: 'SecretId',
          secretKey: 'SecretKey',
          zone: '所在区域 Zone',
          accessKey: 'AccessKey',
          domain: '访问域名',
          customDomain: '自定义域名'
        }
      }
    }
  },
  form: {
    required: '不能为空',
    userName: {
      required: '请输入用户名',
      invalid: '用户名格式不正确'
    },
    phone: {
      required: '请输入手机号',
      invalid: '手机号格式不正确'
    },
    pwd: {
      required: '请输入密码',
      invalid: '密码格式不正确，6-18位字符，包含字母、数字、下划线'
    },
    confirmPwd: {
      required: '请输入确认密码',
      invalid: '两次输入密码不一致'
    },
    code: {
      required: '请输入验证码',
      invalid: '验证码格式不正确'
    },
    email: {
      required: '请输入邮箱',
      invalid: '邮箱格式不正确'
    }
  },
  dropdown: {
    closeCurrent: '关闭',
    closeOther: '关闭其它',
    closeLeft: '关闭左侧',
    closeRight: '关闭右侧',
    closeAll: '关闭所有',
    pin: '固定标签',
    unpin: '取消固定'
  },
  icon: {
    themeConfig: '主题配置',
    themeSchema: '主题模式',
    lang: '切换语言',
    fullscreen: '全屏',
    fullscreenExit: '退出全屏',
    reload: '刷新页面',
    collapse: '折叠菜单',
    expand: '展开菜单',
    pin: '固定',
    unpin: '取消固定'
  },
  datatable: {
    itemCount: '共 {total} 条',
    fixed: {
      left: '左固定',
      right: '右固定',
      unFixed: '取消固定'
    }
  }
};

export default local;
