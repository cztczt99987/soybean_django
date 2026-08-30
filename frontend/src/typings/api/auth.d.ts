declare namespace Api {
  /**
   * namespace Auth
   *
   * backend api module: "auth"
   */
  namespace Auth {
    interface LoginToken {
      token: string;
      refreshToken: string;
    }

    /** 图形验证码 */
    interface Captcha {
      /** 验证码 key，登录时回传 */
      key: string;
      /** SVG 图片字符串 */
      svg: string;
    }

    interface UserInfo {
      userId: string;
      userName: string;
      roles: string[];
      buttons: string[];
    }
  }
}
