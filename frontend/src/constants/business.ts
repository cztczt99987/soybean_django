/**
 * Business constants of system management module
 *
 * 与后端字典数据对应的业务枚举及选项（文案走 i18n key）
 */
import { transformRecordToOption } from '@/utils/common';

/**
 * Enable status
 *
 * - "1": enabled 正常
 * - "0": disabled 停用
 */
export type EnableStatus = '1' | '0';

export const enableStatusRecord: Record<EnableStatus, App.I18n.I18nKey> = {
  '1': 'page.system.common.enabled',
  '0': 'page.system.common.disabled'
};

export const enableStatusOptions = transformRecordToOption(enableStatusRecord);

/**
 * User gender
 *
 * - "0": unknown
 * - "1": male
 * - "2": female
 */
export type UserGender = '0' | '1' | '2';

export const userGenderRecord: Record<UserGender, App.I18n.I18nKey> = {
  '0': 'page.system.common.gender.unknown',
  '1': 'page.system.common.gender.male',
  '2': 'page.system.common.gender.female'
};

export const userGenderOptions = transformRecordToOption(userGenderRecord);

/**
 * Menu type
 *
 * - "1": directory
 * - "2": menu
 * - "3": button
 */
export type MenuType = '1' | '2' | '3';

export const menuTypeRecord: Record<MenuType, App.I18n.I18nKey> = {
  '1': 'page.system.common.menuType.dir',
  '2': 'page.system.common.menuType.menu',
  '3': 'page.system.common.menuType.button'
};

export const menuTypeOptions = transformRecordToOption(menuTypeRecord);

/** config value type */
export type ConfigValueType = 'S' | 'N' | 'B' | 'J';

export const valueTypeRecord: Record<ConfigValueType, App.I18n.I18nKey> = {
  S: 'page.system.common.valueType.S',
  N: 'page.system.common.valueType.N',
  B: 'page.system.common.valueType.B',
  J: 'page.system.common.valueType.J'
};

export const valueTypeOptions = transformRecordToOption(valueTypeRecord);

/** role data scope */
export type DataScope = '1' | '2' | '3' | '4' | '5';

export const dataScopeRecord: Record<DataScope, App.I18n.I18nKey> = {
  '1': 'page.system.common.dataScope.all',
  '2': 'page.system.common.dataScope.custom',
  '3': 'page.system.common.dataScope.dept',
  '4': 'page.system.common.dataScope.deptAndChildren',
  '5': 'page.system.common.dataScope.self'
};

export const dataScopeOptions = transformRecordToOption(dataScopeRecord);

/** operation log type */
export type OperationType = '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9';

export const operationTypeRecord: Record<OperationType, App.I18n.I18nKey> = {
  '1': 'page.system.common.operationType.other',
  '2': 'page.system.common.operationType.create',
  '3': 'page.system.common.operationType.update',
  '4': 'page.system.common.operationType.remove',
  '5': 'page.system.common.operationType.grant',
  '6': 'page.system.common.operationType.export',
  '7': 'page.system.common.operationType.import',
  '8': 'page.system.common.operationType.login',
  '9': 'page.system.common.operationType.logout'
};

export const operationTypeOptions = transformRecordToOption(operationTypeRecord);
