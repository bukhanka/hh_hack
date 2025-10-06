import { CSSProperties, memo } from 'react';

type MoneyElement = {
  type: 'bill' | 'coin';
  size: number;
  startX: number;
  endX: number;
  duration: number;
  delay: number;
  rotateStart: number;
  rotateEnd: number;
  opacity: number;
  tilt: number;
  drift: number;
  scale: number;
  blur: number;
  depth: number;
};

type MoneyStyle = CSSProperties & Record<string, string | number>;

type BillProps = {
  width: number;
  index: number;
};

type CoinProps = {
  size: number;
  index: number;
};

const moneyElements: MoneyElement[] = [
  // Левая сторона экрана
  { type: 'bill', size: 180, startX: 2, endX: 5, duration: 28, delay: 0, rotateStart: -18, rotateEnd: 22, opacity: 0.6, tilt: 8, drift: 15, scale: 1, blur: 0.3, depth: 0 },
  { type: 'coin', size: 90, startX: 5, endX: 8, duration: 22, delay: 2, rotateStart: -8, rotateEnd: 28, opacity: 0.7, tilt: 12, drift: 12, scale: 0.95, blur: 0.2, depth: 0 },
  { type: 'bill', size: 160, startX: 8, endX: 10, duration: 26, delay: 4, rotateStart: -12, rotateEnd: 26, opacity: 0.55, tilt: 9, drift: 18, scale: 0.9, blur: 0.4, depth: 0 },
  { type: 'coin', size: 85, startX: 3, endX: 6, duration: 20, delay: 1, rotateStart: 5, rotateEnd: 35, opacity: 0.65, tilt: 14, drift: 14, scale: 0.95, blur: 0.3, depth: 0 },
  { type: 'bill', size: 170, startX: 1, endX: 4, duration: 30, delay: 3.5, rotateStart: -22, rotateEnd: 14, opacity: 0.5, tilt: 7, drift: 16, scale: 0.88, blur: 0.5, depth: 0 },
  { type: 'coin', size: 95, startX: 6, endX: 9, duration: 24, delay: 6, rotateStart: -14, rotateEnd: 18, opacity: 0.68, tilt: 11, drift: 13, scale: 1, blur: 0.25, depth: 0 },
  
  // Правая сторона экрана
  { type: 'bill', size: 175, startX: 88, endX: 85, duration: 27, delay: 1.5, rotateStart: -10, rotateEnd: 30, opacity: 0.58, tilt: 8, drift: -18, scale: 0.92, blur: 0.35, depth: 0 },
  { type: 'coin', size: 88, startX: 92, endX: 90, duration: 25, delay: 0.5, rotateStart: 3, rotateEnd: 32, opacity: 0.7, tilt: 13, drift: -15, scale: 0.98, blur: 0.2, depth: 0 },
  { type: 'bill', size: 165, startX: 90, endX: 87, duration: 32, delay: 4.5, rotateStart: -16, rotateEnd: 24, opacity: 0.53, tilt: 6, drift: -20, scale: 0.9, blur: 0.45, depth: 0 },
  { type: 'coin', size: 92, startX: 94, endX: 91, duration: 23, delay: 7, rotateStart: -6, rotateEnd: 20, opacity: 0.72, tilt: 10, drift: -16, scale: 1.02, blur: 0.3, depth: 0 },
  { type: 'bill', size: 170, startX: 89, endX: 86, duration: 29, delay: 8, rotateStart: -14, rotateEnd: 20, opacity: 0.56, tilt: 7, drift: -17, scale: 0.93, blur: 0.4, depth: 0 },
  { type: 'coin', size: 80, startX: 93, endX: 89, duration: 21, delay: 9.5, rotateStart: -10, rotateEnd: 22, opacity: 0.66, tilt: 11, drift: -14, scale: 0.9, blur: 0.35, depth: 0 },
];

const Bill = ({ width, index }: BillProps) => {
  const height = Math.round(width * 0.48);
  const gradientId = `money-bill-gradient-${index}`;
  const textureId = `money-bill-texture-${index}`;
  const highlightId = `money-bill-highlight-${index}`;
  const patternId = `money-bill-pattern-${index}`;

  return (
    <svg
      className="money-icon-svg"
      width={width}
      height={height}
      viewBox="0 0 200 96"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        {/* Зеленый градиент доллара */}
        <linearGradient id={gradientId} x1="0" y1="0" x2="200" y2="96" gradientUnits="userSpaceOnUse">
          <stop stopColor="#2d5016" stopOpacity="0.95" />
          <stop offset="0.5" stopColor="#3d7c1f" stopOpacity="0.9" />
          <stop offset="1" stopColor="#4d9922" stopOpacity="0.85" />
        </linearGradient>
        {/* Текстура бумаги */}
        <radialGradient id={textureId} cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(100 48) scale(100 48)">
          <stop stopColor="#6db33f" stopOpacity="0.3" />
          <stop offset="1" stopColor="#2d5016" stopOpacity="0.1" />
        </radialGradient>
        {/* Паттерн для фона */}
        <pattern id={patternId} x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
          <circle cx="10" cy="10" r="1" fill="rgba(157, 233, 109, 0.15)" />
        </pattern>
        {/* Блик */}
        <linearGradient id={highlightId} x1="0" y1="0" x2="200" y2="0" gradientUnits="userSpaceOnUse">
          <stop stopColor="rgba(255, 255, 255, 0.2)" />
          <stop offset="0.5" stopColor="rgba(255, 255, 255, 0)" />
          <stop offset="1" stopColor="rgba(255, 255, 255, 0.15)" />
        </linearGradient>
      </defs>

      {/* Основа купюры */}
      <rect x="2" y="2" width="196" height="92" rx="8" fill={`url(#${gradientId})`} stroke="#1a3d0f" strokeWidth="2" />
      
      {/* Текстура и паттерн */}
      <rect x="4" y="4" width="192" height="88" rx="6" fill={`url(#${textureId})`} />
      <rect x="4" y="4" width="192" height="88" rx="6" fill={`url(#${patternId})`} />
      
      {/* Декоративные углы */}
      <path d="M15 15 Q20 15 20 20" stroke="#9de96d" strokeWidth="2" fill="none" />
      <path d="M185 15 Q180 15 180 20" stroke="#9de96d" strokeWidth="2" fill="none" />
      <path d="M15 81 Q20 81 20 76" stroke="#9de96d" strokeWidth="2" fill="none" />
      <path d="M185 81 Q180 81 180 76" stroke="#9de96d" strokeWidth="2" fill="none" />
      
      {/* Центральный овал для "портрета" */}
      <ellipse cx="100" cy="48" rx="28" ry="32" fill="#1a3d0f" opacity="0.6" />
      <ellipse cx="100" cy="48" rx="26" ry="30" fill="none" stroke="#9de96d" strokeWidth="2" />
      
      {/* Упрощенный "портрет" */}
      <circle cx="100" cy="42" r="10" fill="#9de96d" opacity="0.7" />
      <ellipse cx="100" cy="58" rx="14" ry="10" fill="#9de96d" opacity="0.7" />
      
      {/* Номинал слева */}
      <text x="35" y="58" fontSize="32" fontWeight="bold" fill="#9de96d" fontFamily="serif">$</text>
      
      {/* Номинал справа */}
      <text x="155" y="58" fontSize="32" fontWeight="bold" fill="#9de96d" fontFamily="serif">$</text>
      
      {/* Серийный номер (имитация) */}
      <rect x="15" y="12" width="60" height="8" rx="2" fill="#1a3d0f" opacity="0.4" />
      <rect x="125" y="76" width="60" height="8" rx="2" fill="#1a3d0f" opacity="0.4" />
      
      {/* Декоративные линии */}
      <path d="M30 30 L60 30" stroke="#9de96d" strokeWidth="1.5" opacity="0.5" />
      <path d="M30 66 L60 66" stroke="#9de96d" strokeWidth="1.5" opacity="0.5" />
      <path d="M140 30 L170 30" stroke="#9de96d" strokeWidth="1.5" opacity="0.5" />
      <path d="M140 66 L170 66" stroke="#9de96d" strokeWidth="1.5" opacity="0.5" />
      
      {/* Блик сверху */}
      <rect x="4" y="4" width="192" height="20" rx="6" fill={`url(#${highlightId})`} />
    </svg>
  );
};

const Coin = ({ size, index }: CoinProps) => {
  const gradientId = `money-coin-gradient-${index}`;
  const ringId = `money-coin-ring-${index}`;
  const shineId = `money-coin-shine-${index}`;
  const isGold = index % 3 !== 2; // 2 из 3 монет - золотые

  return (
    <svg
      className="money-icon-svg"
      width={size}
      height={size}
      viewBox="0 0 120 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        {/* Градиент для золотых/серебряных монет */}
        <radialGradient id={gradientId} cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(60 60) scale(60)">
          {isGold ? (
            <>
              <stop offset="0" stopColor="#ffd700" stopOpacity="0.95" />
              <stop offset="0.3" stopColor="#ffed4e" stopOpacity="0.9" />
              <stop offset="0.7" stopColor="#d4af37" stopOpacity="0.88" />
              <stop offset="1" stopColor="#b8860b" stopOpacity="0.85" />
            </>
          ) : (
            <>
              <stop offset="0" stopColor="#e8e8e8" stopOpacity="0.95" />
              <stop offset="0.3" stopColor="#f5f5f5" stopOpacity="0.9" />
              <stop offset="0.7" stopColor="#c0c0c0" stopOpacity="0.88" />
              <stop offset="1" stopColor="#a8a8a8" stopOpacity="0.85" />
            </>
          )}
        </radialGradient>
        {/* Градиент для ободка */}
        <linearGradient id={ringId} x1="20" y1="20" x2="100" y2="100" gradientUnits="userSpaceOnUse">
          {isGold ? (
            <>
              <stop stopColor="#ffed4e" stopOpacity="0.9" />
              <stop offset="0.5" stopColor="#d4af37" stopOpacity="0.8" />
              <stop offset="1" stopColor="#8b6914" stopOpacity="0.7" />
            </>
          ) : (
            <>
              <stop stopColor="#f5f5f5" stopOpacity="0.9" />
              <stop offset="0.5" stopColor="#c0c0c0" stopOpacity="0.8" />
              <stop offset="1" stopColor="#808080" stopOpacity="0.7" />
            </>
          )}
        </linearGradient>
        {/* Блик */}
        <radialGradient id={shineId} cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(45 45) scale(35)">
          <stop offset="0" stopColor="rgba(255, 255, 255, 0.6)" />
          <stop offset="1" stopColor="rgba(255, 255, 255, 0)" />
        </radialGradient>
      </defs>

      {/* Основа монеты */}
      <circle cx="60" cy="60" r="56" fill={`url(#${gradientId})`} />
      
      {/* Внешний ободок */}
      <circle cx="60" cy="60" r="56" stroke={`url(#${ringId})`} strokeWidth="3" opacity="0.9" />
      
      {/* Рельефный ободок */}
      <circle cx="60" cy="60" r="50" stroke={isGold ? '#b8860b' : '#a0a0a0'} strokeWidth="2" opacity="0.6" />
      <circle cx="60" cy="60" r="47" stroke={isGold ? '#d4af37' : '#c8c8c8'} strokeWidth="1.5" opacity="0.4" />
      
      {/* Центральная область */}
      <circle cx="60" cy="60" r="42" fill={isGold ? 'rgba(212, 175, 55, 0.3)' : 'rgba(192, 192, 192, 0.3)'} />
      
      {/* Профиль (упрощенный) */}
      <ellipse cx="56" cy="60" rx="18" ry="24" fill={isGold ? 'rgba(184, 134, 11, 0.5)' : 'rgba(128, 128, 128, 0.5)'} />
      <circle cx="56" cy="52" r="8" fill={isGold ? 'rgba(139, 105, 20, 0.6)' : 'rgba(96, 96, 96, 0.6)'} />
      <ellipse cx="56" cy="68" rx="10" ry="8" fill={isGold ? 'rgba(139, 105, 20, 0.6)' : 'rgba(96, 96, 96, 0.6)'} />
      
      {/* Надпись "LIBERTY" (имитация) */}
      <path 
        d="M30 35 Q60 32 90 35" 
        stroke={isGold ? '#8b6914' : '#606060'} 
        strokeWidth="2.5" 
        fill="none"
        opacity="0.7"
      />
      
      {/* Надпись "IN GOD WE TRUST" (имитация) */}
      <path 
        d="M35 85 Q60 87 85 85" 
        stroke={isGold ? '#8b6914' : '#606060'} 
        strokeWidth="2" 
        fill="none"
        opacity="0.7"
      />
      
      {/* Декоративные звезды */}
      <circle cx="85" cy="50" r="2" fill={isGold ? '#8b6914' : '#606060'} opacity="0.6" />
      <circle cx="85" cy="70" r="2" fill={isGold ? '#8b6914' : '#606060'} opacity="0.6" />
      
      {/* Год (имитация) */}
      <rect x="48" y="88" width="24" height="6" rx="1" fill={isGold ? 'rgba(139, 105, 20, 0.5)' : 'rgba(96, 96, 96, 0.5)'} />
      
      {/* Блик света */}
      <ellipse cx="45" cy="45" rx="20" ry="25" fill={`url(#${shineId})`} />
    </svg>
  );
};

const MoneyBackground = () => (
  <div className="money-scene" aria-hidden>
    {moneyElements.map((item, index) => {
      const width = item.size;
      const height = item.type === 'coin' ? item.size : Math.round(item.size * 0.48);
      const midpoint = (item.startX + item.endX) / 2;
      const midRotation = (item.rotateStart + item.rotateEnd) / 2;

      const style: MoneyStyle = {
        width,
        height,
        zIndex: item.depth,
        '--delay': `${item.delay}s`,
        '--duration': `${item.duration}s`,
        '--opacity-target': item.opacity.toString(),
        '--start-offset': `${item.startX}vw`,
        '--mid-offset': `${midpoint}vw`,
        '--end-offset': `${item.endX}vw`,
        '--rotate-start': `${item.rotateStart}deg`,
        '--mid-rotation': `${midRotation}deg`,
        '--rotate-end': `${item.rotateEnd}deg`,
        '--scale': item.scale.toString(),
        '--tilt': `${item.tilt}deg`,
        '--drift': `${item.drift}px`,
        '--blur': `${item.blur}px`,
      };

      return (
        <div key={index} className="money-item" style={style}>
          <div className="money-item__inner">
            <div className={`money-item__icon ${item.type === 'coin' ? 'money-item__icon--coin' : 'money-item__icon--bill'}`}>
              {item.type === 'bill' ? <Bill width={width} index={index} /> : <Coin size={width} index={index} />}
            </div>
          </div>
        </div>
      );
    })}
  </div>
);

export default memo(MoneyBackground);
