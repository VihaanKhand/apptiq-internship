export enum ModelId {
  GEMINI_2_0_FLASH = 'gemini-2.0-flash',
  GEMINI_2_5_FLASH_PREVIEW = 'gemini-2.5-flash-preview-04-17',
  GEMINI_2_5_PRO_PREVIEW = 'gemini-2.5-pro-preview-05-06',
}

export interface Model {
  id: ModelId;
  name: string;
  description: string;
  icon: string;
  iconColor: string;
}

export const AVAILABLE_MODELS: Model[] = [
  {
    id: ModelId.GEMINI_2_0_FLASH,
    name: '2.0 Flash',
    description: 'Fast and efficient for most tasks',
    icon: 'zap',
    iconColor: 'text-yellow-400',
  },
  {
    id: ModelId.GEMINI_2_5_FLASH_PREVIEW,
    name: '2.5 Flash',
    description: 'Enhanced performance with faster response',
    icon: 'zap',
    iconColor: 'text-orange-400',
  },
  {
    id: ModelId.GEMINI_2_5_PRO_PREVIEW,
    name: '2.5 Pro',
    description: 'Most capable model for complex tasks',
    icon: 'cpu',
    iconColor: 'text-purple-400',
  },
];

export const DEFAULT_MODEL = ModelId.GEMINI_2_0_FLASH;
