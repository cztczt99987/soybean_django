import { request } from '../request';

/**
 * Login
 *
 * @param userName User name
 * @param password Password
 * @param captchaKey Captcha key from `/auth/captcha`
 * @param captchaCode User input captcha code
 */
export function fetchLogin(userName: string, password: string, captchaKey: string, captchaCode: string) {
  return request<Api.Auth.LoginToken>({
    url: '/auth/login',
    method: 'post',
    data: {
      userName,
      password,
      captchaKey,
      captchaCode
    }
  });
}

/** Get image captcha */
export function fetchCaptcha() {
  return request<Api.Auth.Captcha>({ url: '/auth/captcha' });
}

/** Get user info */
export function fetchGetUserInfo() {
  return request<Api.Auth.UserInfo>({ url: '/auth/getUserInfo' });
}

/**
 * Refresh token
 *
 * @param refreshToken Refresh token
 */
export function fetchRefreshToken(refreshToken: string) {
  return request<Api.Auth.LoginToken>({
    url: '/auth/refreshToken',
    method: 'post',
    data: {
      refreshToken
    }
  });
}

/**
 * return custom backend error
 *
 * @param code error code
 * @param msg error message
 */
export function fetchCustomBackendError(code: string, msg: string) {
  return request({ url: '/auth/error', params: { code, msg } });
}
