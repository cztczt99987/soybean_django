const local: App.I18n.Schema = {
  system: {
    title: 'SoybeanAdmin',
    updateTitle: 'System Version Update Notification',
    updateContent: 'A new version of the system has been detected. Do you want to refresh the page immediately?',
    updateConfirm: 'Refresh immediately',
    updateCancel: 'Later'
  },
  common: {
    action: 'Action',
    add: 'Add',
    addSuccess: 'Add Success',
    addChildMenu: 'Add Child Menu',
    addChildDept: 'Add Child Dept',
    backToHome: 'Back to home',
    batchDelete: 'Batch Delete',
    cancel: 'Cancel',
    close: 'Close',
    check: 'Check',
    selectAll: 'Select All',
    expandColumn: 'Expand Column',
    columnSetting: 'Column Setting',
    config: 'Config',
    confirm: 'Confirm',
    delete: 'Delete',
    deleteSuccess: 'Delete Success',
    confirmDelete: 'Are you sure you want to delete?',
    edit: 'Edit',
    warning: 'Warning',
    error: 'Error',
    iconPicker: {
      title: 'Select Icon',
      search: 'Search icon',
      clear: 'Clear',
      categories: {
        common: 'Common',
        system: 'System',
        user: 'User',
        file: 'File',
        edit: 'Edit',
        chart: 'Chart',
        message: 'Message',
        navigate: 'Navigation'
      }
    },
    index: 'Index',
    keywordSearch: 'Please enter keyword',
    logout: 'Logout',
    logoutConfirm: 'Are you sure you want to log out?',
    lookForward: 'Coming soon',
    modify: 'Modify',
    modifySuccess: 'Modify Success',
    noData: 'No Data',
    operate: 'Operate',
    pleaseCheckValue: 'Please check whether the value is valid',
    refresh: 'Refresh',
    reset: 'Reset',
    search: 'Search',
    switch: 'Switch',
    tip: 'Tip',
    trigger: 'Trigger',
    update: 'Update',
    updateSuccess: 'Update Success',
    userCenter: 'User Center',
    yesOrNo: {
      yes: 'Yes',
      no: 'No'
    }
  },
  request: {
    logout: 'Logout user after request failed',
    logoutMsg: 'User status is invalid, please log in again',
    logoutWithModal: 'Pop up modal after request failed and then log out user',
    logoutWithModalMsg: 'User status is invalid, please log in again',
    refreshToken: 'The requested token has expired, refresh the token',
    tokenExpired: 'The requested token has expired'
  },
  theme: {
    themeDrawerTitle: 'Theme Configuration',
    tabs: {
      appearance: 'Appearance',
      layout: 'Layout',
      general: 'General',
      preset: 'Preset'
    },
    appearance: {
      themeSchema: {
        title: 'Theme Schema',
        light: 'Light',
        dark: 'Dark',
        auto: 'Follow System'
      },
      grayscale: 'Grayscale',
      colourWeakness: 'Colour Weakness',
      themeColor: {
        title: 'Theme Color',
        primary: 'Primary',
        info: 'Info',
        success: 'Success',
        warning: 'Warning',
        error: 'Error',
        followPrimary: 'Follow Primary'
      },
      themeRadius: {
        title: 'Theme Radius'
      },
      recommendColor: 'Apply Recommended Color Algorithm',
      recommendColorDesc: 'The recommended color algorithm refers to',
      preset: {
        title: 'Theme Presets',
        apply: 'Apply',
        applySuccess: 'Preset applied successfully',
        default: {
          name: 'Default Preset',
          desc: 'Default theme preset with balanced settings'
        },
        dark: {
          name: 'Dark Preset',
          desc: 'Dark theme preset for night time usage'
        },
        compact: {
          name: 'Compact Preset',
          desc: 'Compact layout preset for small screens'
        },
        azir: {
          name: "Azir's Preset",
          desc: 'It is a cold and elegant preset that Azir likes'
        }
      }
    },
    layout: {
      layoutMode: {
        title: 'Layout Mode',
        vertical: 'Vertical Mode',
        horizontal: 'Horizontal Mode',
        'vertical-mix': 'Vertical Mix Mode',
        'vertical-hybrid-header-first': 'Left Hybrid Header-First',
        'top-hybrid-sidebar-first': 'Top-Hybrid Sidebar-First',
        'top-hybrid-header-first': 'Top-Hybrid Header-First',
        vertical_detail: 'Vertical menu layout, with the menu on the left and content on the right.',
        'vertical-mix_detail':
          'Vertical mix-menu layout, with the primary menu on the dark left side and the secondary menu on the lighter left side.',
        'vertical-hybrid-header-first_detail':
          'Left hybrid layout, with the primary menu at the top, the secondary menu on the dark left side, and the tertiary menu on the lighter left side.',
        horizontal_detail: 'Horizontal menu layout, with the menu at the top and content below.',
        'top-hybrid-sidebar-first_detail':
          'Top hybrid layout, with the primary menu on the left and the secondary menu at the top.',
        'top-hybrid-header-first_detail':
          'Top hybrid layout, with the primary menu at the top and the secondary menu on the left.'
      },
      tab: {
        title: 'Tab Settings',
        visible: 'Tab Visible',
        cache: 'Tag Bar Info Cache',
        cacheTip: 'Keep the tab bar information after leaving the page',
        height: 'Tab Height',
        mode: {
          title: 'Tab Mode',
          slider: 'Slider',
          chrome: 'Chrome',
          button: 'Button'
        },
        closeByMiddleClick: 'Close Tab by Middle Click',
        closeByMiddleClickTip: 'Enable closing tabs by clicking with the middle mouse button'
      },
      header: {
        title: 'Header Settings',
        height: 'Header Height',
        breadcrumb: {
          visible: 'Breadcrumb Visible',
          showIcon: 'Breadcrumb Icon Visible'
        }
      },
      sider: {
        title: 'Sider Settings',
        inverted: 'Dark Sider',
        width: 'Sider Width',
        collapsedWidth: 'Sider Collapsed Width',
        mixWidth: 'Mix Sider Width',
        mixCollapsedWidth: 'Mix Sider Collapse Width',
        mixChildMenuWidth: 'Mix Child Menu Width',
        autoSelectFirstMenu: 'Auto Select First Submenu',
        autoSelectFirstMenuTip:
          'When a first-level menu is clicked, the first submenu is automatically selected and navigated to the deepest level'
      },
      footer: {
        title: 'Footer Settings',
        visible: 'Footer Visible',
        fixed: 'Fixed Footer',
        height: 'Footer Height',
        right: 'Right Footer'
      },
      content: {
        title: 'Content Area Settings',
        scrollMode: {
          title: 'Scroll Mode',
          tip: 'The theme scroll only scrolls the main part, the outer scroll can carry the header and footer together',
          wrapper: 'Wrapper',
          content: 'Content'
        },
        page: {
          animate: 'Page Animate',
          mode: {
            title: 'Page Animate Mode',
            fade: 'Fade',
            'fade-slide': 'Slide',
            'fade-bottom': 'Fade Zoom',
            'fade-scale': 'Fade Scale',
            'zoom-fade': 'Zoom Fade',
            'zoom-out': 'Zoom Out',
            none: 'None'
          }
        },
        fixedHeaderAndTab: 'Fixed Header And Tab'
      }
    },
    general: {
      title: 'General Settings',
      watermark: {
        title: 'Watermark Settings',
        visible: 'Watermark Full Screen Visible',
        text: 'Custom Watermark Text',
        enableUserName: 'Enable User Name Watermark',
        enableTime: 'Show Current Time',
        timeFormat: 'Time Format'
      },
      multilingual: {
        title: 'Multilingual Settings',
        visible: 'Display multilingual button'
      },
      globalSearch: {
        title: 'Global Search Settings',
        visible: 'Display GlobalSearch button'
      }
    },
    configOperation: {
      copyConfig: 'Copy Config',
      copySuccessMsg: 'Copy Success, Please replace the variable "themeSettings" in "src/theme/settings.ts"',
      resetConfig: 'Reset Config',
      resetSuccessMsg: 'Reset Success'
    }
  },
  route: {
    login: 'Login',
    403: 'No Permission',
    404: 'Page Not Found',
    500: 'Server Error',
    'iframe-page': 'Iframe',
    home: 'Home',
    'system': 'System',
    'system_config': 'Configs',
    'system_dept': 'Departments',
    'system_dict': 'Dictionary',
    'system_log': 'Operation Logs',
    'system_menu': 'Menus',
    'system_post': 'Posts',
    'system_role': 'Roles',
    'system_user': 'Users',
    'monitor': 'Monitor',
    'monitor_server': 'Server Info',
    'monitor_cache': 'Cache Monitor',
    'monitor_file': 'File Manager',
  },
  page: {
    login: {
      common: {
        loginOrRegister: 'Login / Register',
        userNamePlaceholder: 'Please enter user name',
        phonePlaceholder: 'Please enter phone number',
        codePlaceholder: 'Please enter verification code',
        passwordPlaceholder: 'Please enter password',
        confirmPasswordPlaceholder: 'Please enter password again',
        codeLogin: 'Verification code login',
        confirm: 'Confirm',
        back: 'Back',
        validateSuccess: 'Verification passed',
        loginSuccess: 'Login successfully',
        welcomeBack: 'Welcome back, {userName} !'
      },
      pwdLogin: {
        title: 'Password Login',
        rememberMe: 'Remember me',
        forgetPassword: 'Forget password?',
        register: 'Register',
        otherAccountLogin: 'Other Account Login',
        otherLoginMode: 'Other Login Mode',
        superAdmin: 'Super Admin',
        admin: 'Admin',
        user: 'User'
      },
      codeLogin: {
        title: 'Verification Code Login',
        getCode: 'Get verification code',
        reGetCode: 'Reacquire after {time}s',
        sendCodeSuccess: 'Verification code sent successfully',
        imageCodePlaceholder: 'Please enter image verification code'
      },
      register: {
        title: 'Register',
        agreement: 'I have read and agree to',
        protocol: '《User Agreement》',
        policy: '《Privacy Policy》'
      },
      resetPwd: {
        title: 'Reset Password'
      },
      bindWeChat: {
        title: 'Bind WeChat'
      }
    },
    home: {
      branchDesc:
        'For the convenience of everyone in developing and updating the merge, we have streamlined the code of the main branch, only retaining the homepage menu, and the rest of the content has been moved to the example branch for maintenance. The preview address displays the content of the example branch.',
      greeting: 'Good morning, {userName}, today is another day full of vitality!',
      weatherDesc: 'Today is cloudy to clear, 20℃ - 25℃!',
      projectCount: 'Project Count',
      todo: 'Todo',
      message: 'Message',
      downloadCount: 'Download Count',
      registerCount: 'Register Count',
      schedule: 'Work and rest Schedule',
      study: 'Study',
      work: 'Work',
      rest: 'Rest',
      entertainment: 'Entertainment',
      visitCount: 'Visit Count',
      turnover: 'Turnover',
      dealCount: 'Deal Count',
      projectNews: {
        title: 'Project News',
        moreNews: 'More News',
        desc1: 'Soybean created the open source project soybean-admin on May 28, 2021!',
        desc2: 'Yanbowe submitted a bug to soybean-admin, the multi-tab bar will not adapt.',
        desc3: 'Soybean is ready to do sufficient preparation for the release of soybean-admin!',
        desc4: 'Soybean is busy writing project documentation for soybean-admin!',
        desc5: 'Soybean just wrote some of the workbench pages casually, and it was enough to see!'
      },
      creativity: 'Creativity'
    },
    system: {
      user: {
        title: 'User Management',
        form: { username: 'Username', nickname: 'Nickname', password: 'Initial Password', email: 'Email', phone: 'Phone', gender: 'Gender', dept: 'Department', roles: 'Roles', posts: 'Posts', status: 'Status', remark: 'Remark' },
        action: { resetPwd: 'Reset Password', changeStatus: 'Enable/Disable' }
      },
      role: {
        title: 'Role Management',
        form: { name: 'Role Name', code: 'Role Code', dataScope: 'Data Scope', menus: 'Menu Permissions', departments: 'Data Scope Departments', status: 'Status', remark: 'Remark' },
        action: { assignMenus: 'Assign Menus' }
      },
      menu: {
        title: 'Menu Management',
        form: { parent: 'Parent Menu', name: 'Route Name', title: 'Display Name', path: 'Route Path', component: 'Component Path', permission: 'Permission', icon: 'Icon', type: 'Type', order: 'Sort Order', i18nKey: 'i18n Key', keepAlive: 'Keep Alive', hideInMenu: 'Hide in Menu', externalLink: 'External Link', status: 'Status', remark: 'Remark' }
      },
      dept: {
        title: 'Department Management',
        form: { parent: 'Parent Department', name: 'Department Name', code: 'Department Code', leader: 'Leader', phone: 'Phone', email: 'Email', status: 'Status', remark: 'Remark' }
      },
      post: {
        title: 'Post Management',
        form: { name: 'Post Name', code: 'Post Code', status: 'Status', sortOrder: 'Sort Order', remark: 'Remark' }
      },
      dict: {
        title: 'Dictionary Management',
        typeTab: 'Dictionary Type',
        dataTab: 'Dictionary Data',
        selectTypePlaceholder: 'Please select a dictionary type',
        selectTypeFirst: 'Please select a dictionary type first',
        form: { name: 'Dictionary Name', code: 'Dictionary Code', status: 'Status', remark: 'Remark' },
        data: { label: 'Label', value: 'Value', cssClass: 'CSS Class', listClass: 'List Class', isDefault: 'Is Default', status: 'Status', remark: 'Remark' }
      },
      config: {
        title: 'Config Management',
        form: { name: 'Config Name', code: 'Config Key', value: 'Config Value', valueType: 'Value Type', isSystem: 'System Built-in', status: 'Status', remark: 'Remark' }
      },
      log: {
        title: 'Log Management',
        fields: { username: 'Username', module: 'Module', description: 'Description', operationType: 'Operation Type', method: 'Method', url: 'URL', ip: 'IP', status: 'Status', costTime: 'Cost Time', operatedAt: 'Operated At', dateRange: 'Date Range' },
        action: { clean: 'Clean N Days Ago', cleanTitle: 'Clean Logs', cleanDays: 'Clean logs older than specified days', day: 'Days' }
      },
      common: {
        createdAt: 'Created At',
        enabled: 'Enabled',
        disabled: 'Disabled',
        success: 'Success',
        failure: 'Failure',
        gender: { unknown: 'Unknown', male: 'Male', female: 'Female' },
        valueType: { S: 'String', N: 'Number', B: 'Boolean', J: 'JSON' },
        menuType: { dir: 'Directory', menu: 'Menu', button: 'Button' },
        dataScope: { all: 'All Data', custom: 'Custom Data', dept: 'Dept Data', deptAndChildren: 'Dept & Children Data', self: 'Self Data Only' },
        operationType: { other: 'Other', create: 'Create', update: 'Update', remove: 'Remove', grant: 'Grant', export: 'Export', import: 'Import', login: 'Login', logout: 'Logout' },
        resetPwdSuccess: 'Password reset successfully',
        resetPwdConfirm: 'Are you sure you want to reset the password?',
        changeStatusSuccess: 'Status changed successfully',
        assignMenusSuccess: 'Menus assigned successfully',
        cleanSuccess: 'Cleaned successfully',
        dateRange: 'Date Range'
      }
    },
    monitor: {
      server: {
        title: 'Server Info',
        refresh: 'Refresh',
        basic: 'Basic Info',
        os: 'Operating System',
        hostname: 'Hostname',
        osName: 'OS Name',
        osVersion: 'OS Version',
        osRelease: 'Kernel Release',
        arch: 'Architecture',
        cpuModel: 'CPU Model',
        pythonVersion: 'Python Version',
        djangoVersion: 'Django Version',
        bootTime: 'Boot Time',
        uptime: 'Uptime',
        cpu: 'CPU',
        physicalCores: 'Physical Cores',
        logicalCores: 'Logical Cores',
        usage: 'Usage',
        freq: 'Frequency (MHz)',
        memory: 'Memory',
        total: 'Total',
        used: 'Used',
        available: 'Available',
        usagePercent: 'Usage',
        swapTotal: 'Swap Total',
        swapUsed: 'Swap Used',
        swapUsage: 'Swap Usage',
        disk: 'Disk',
        device: 'Device',
        mountpoint: 'Mount Point',
        fstype: 'File System',
        free: 'Free',
        network: 'Network',
        ip: 'Local IP',
        bytesSent: 'Bytes Sent',
        bytesRecv: 'Bytes Recv',
        packetsSent: 'Packets Sent',
        packetsRecv: 'Packets Recv',
        process: 'App Process',
        pid: 'PID'
      },
      cache: {
        title: 'Cache Monitor',
        notRedis: 'Redis is not enabled (in-memory cache mode), cache management is unavailable',
        key: 'Key',
        type: 'Type',
        size: 'Size',
        ttl: 'TTL',
        ttlNone: 'Never',
        serverInfo: 'Redis Info',
        redisVersion: 'Redis Version',
        usedMemory: 'Used Memory',
        maxMemory: 'Max Memory',
        connectedClients: 'Connected Clients',
        dbSize: 'DB Size',
        deleteConfirm: 'Are you sure you want to delete the selected cache keys?',
        cleanAll: 'Clean All',
        cleanAllConfirm: 'Are you sure you want to flush all caches? This action cannot be undone!',
        deleteSuccess: 'Deleted successfully',
        keywordPlaceholder: 'Please enter key keyword'
      },
      file: {
        title: 'File Manager',
        browser: 'File Browser',
        storage: 'Storage Config',
        name: 'Name',
        size: 'Size',
        modified: 'Modified',
        download: 'Download',
        up: 'Parent',
        root: 'Root',
        emptyDir: 'Empty directory',
        activeStorage: 'Active Storage',
        currentActive: 'Currently used storage',
        switchTo: 'Switch to this storage',
        switchConfirm: 'Switch storage? New uploads will use the selected storage',
        switchSuccess: 'Switched successfully',
        save: 'Save Config',
        validate: 'Validate Config',
        saveSuccess: 'Saved successfully',
        validateSuccess: 'Config validated',
        typeLocal: 'Local Storage',
        typeAliyun: 'Aliyun OSS',
        typeTencent: 'Tencent COS',
        typeQiniu: 'Qiniu Kodo',
        fields: {
          basePath: 'Local Base Path',
          endpoint: 'Endpoint',
          bucket: 'Bucket',
          accessKeyId: 'AccessKeyId',
          accessKeySecret: 'AccessKeySecret',
          region: 'Region',
          secretId: 'SecretId',
          secretKey: 'SecretKey',
          zone: 'Zone',
          accessKey: 'AccessKey',
          domain: 'Domain',
          customDomain: 'Custom Domain'
        }
      }
    }
  },
  form: {
    required: 'Cannot be empty',
    userName: {
      required: 'Please enter user name',
      invalid: 'User name format is incorrect'
    },
    phone: {
      required: 'Please enter phone number',
      invalid: 'Phone number format is incorrect'
    },
    pwd: {
      required: 'Please enter password',
      invalid: '6-18 characters, including letters, numbers, and underscores'
    },
    confirmPwd: {
      required: 'Please enter password again',
      invalid: 'The two passwords are inconsistent'
    },
    code: {
      required: 'Please enter verification code',
      invalid: 'Verification code format is incorrect'
    },
    email: {
      required: 'Please enter email',
      invalid: 'Email format is incorrect'
    }
  },
  dropdown: {
    closeCurrent: 'Close Current',
    closeOther: 'Close Other',
    closeLeft: 'Close Left',
    closeRight: 'Close Right',
    closeAll: 'Close All',
    pin: 'Pin Tab',
    unpin: 'Unpin Tab'
  },
  icon: {
    themeConfig: 'Theme Configuration',
    themeSchema: 'Theme Schema',
    lang: 'Switch Language',
    fullscreen: 'Fullscreen',
    fullscreenExit: 'Exit Fullscreen',
    reload: 'Reload Page',
    collapse: 'Collapse Menu',
    expand: 'Expand Menu',
    pin: 'Pin',
    unpin: 'Unpin'
  },
  datatable: {
    itemCount: 'Total {total} items',
    fixed: {
      left: 'Left Fixed',
      right: 'Right Fixed',
      unFixed: 'Unfixed'
    }
  }
};

export default local;
