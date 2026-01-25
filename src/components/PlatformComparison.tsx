import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';

interface Platform {
  name: string;
  score: number;
  problems: string[];
  limitations: string[];
  color: string;
}

const PlatformComparison = () => {
  const platforms: Platform[] = [
    {
      name: 'Tilda',
      score: 3,
      problems: [
        'jQuery 1.10.2 (уязвимости CVE-2019-11358)',
        'Нет экспорта исходного кода',
        'Proprietary block system (vendor lock-in)'
      ],
      limitations: [
        'Только визуальные блоки',
        'ИИ только для контента, не для логики',
        'Нет GitHub интеграции'
      ],
      color: 'bg-red-500'
    },
    {
      name: 'Mixo',
      score: 4,
      problems: [
        'Только статические лендинги',
        'Невозможность добавить базу данных',
        'Нет динамической логики'
      ],
      limitations: [
        'Статика HTML/CSS/JS',
        'No-code ограничения',
        'Нет API генерации'
      ],
      color: 'bg-orange-500'
    },
    {
      name: 'CodeWP',
      score: 4,
      problems: [
        'Только WordPress',
        'PHP-only (устаревший стек)',
        'Уязвимости через плагины WP'
      ],
      limitations: [
        'WordPress-locked',
        'Нет современных фреймворков',
        'Нет headless архитектуры'
      ],
      color: 'bg-orange-500'
    },
    {
      name: 'Lovable.dev',
      score: 5,
      problems: [
        'Неоптимальный код (избыточные re-renders)',
        'Бандлы 2-3MB без tree-shaking',
        'Отсутствие типизации в TS'
      ],
      limitations: [
        'Шаблонная генерация',
        'Только React + Vite',
        'Частичная GitHub синхронизация'
      ],
      color: 'bg-yellow-500'
    },
    {
      name: 'Cursor.com',
      score: 6,
      problems: [
        'Потеря контекста между сессиями',
        'Memory leak при проектах >10K файлов',
        'Конфликты при параллельных правках'
      ],
      limitations: [
        'IDE-only, не платформа',
        'Локальная установка обязательна',
        'Нет встроенного деплоя'
      ],
      color: 'bg-lime-500'
    },
    {
      name: 'poehali.dev',
      score: 7,
      problems: [
        'React hooks conflicts',
        'Backend тесты падают при FK constraints',
        'Radix UI вызывает ошибки'
      ],
      limitations: [
        'Vite + React only',
        'Нет автономности агента',
        'GitHub не автоматизирован'
      ],
      color: 'bg-green-500'
    }
  ];

  const newPlatform = {
    name: 'Новая платформа',
    score: 10,
    features: [
      'Векторная БД + Neo4j (контекст на годы)',
      'Автофикс до 100% прохождения тестов',
      'GitHub: auto PR + CI + auto-merge',
      'Автономные тесты (генерация + запуск + фикс)',
      'Terraform + auto-scaling + SSL',
      'Полный доступ к коду + мультифайловые функции',
      'Pay-per-use: $0.02/1K tokens + $5-50/месяц'
    ],
    metrics: [
      { label: 'Time to Production', value: '<10 мин', icon: 'Clock' },
      { label: 'Code Quality', value: 'A (SonarQube)', icon: 'Award' },
      { label: 'Test Coverage', value: '>85%', icon: 'Target' },
      { label: 'Security Score', value: '100/100', icon: 'Shield' },
      { label: 'Bundle Size', value: '<500 KB', icon: 'Package' },
      { label: 'Deploy Success', value: '>95%', icon: 'TrendingUp' }
    ]
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold mb-2">Сравнение с конкурентами</h2>
        <p className="text-muted-foreground">
          Системные проблемы существующих платформ и их решения
        </p>
      </div>

      {/* Existing platforms */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {platforms.map((platform) => (
          <Card key={platform.name} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{platform.name}</CardTitle>
                <div className="flex items-center gap-2">
                  <div className={`w-12 h-12 rounded-full ${platform.color} flex items-center justify-center text-white font-bold text-xl`}>
                    {platform.score}
                  </div>
                  <span className="text-xs text-muted-foreground">/10</span>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="text-xs font-semibold mb-2 flex items-center gap-1">
                  <Icon name="AlertTriangle" size={14} className="text-red-500" />
                  Критические ошибки:
                </div>
                <ul className="space-y-1">
                  {platform.problems.map((problem, idx) => (
                    <li key={idx} className="text-xs text-muted-foreground flex items-start gap-1">
                      <span className="text-red-500 mt-0.5">×</span>
                      <span>{problem}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <div className="text-xs font-semibold mb-2 flex items-center gap-1">
                  <Icon name="Ban" size={14} className="text-orange-500" />
                  Ограничения:
                </div>
                <ul className="space-y-1">
                  {platform.limitations.map((limitation, idx) => (
                    <li key={idx} className="text-xs text-muted-foreground flex items-start gap-1">
                      <span className="text-orange-500 mt-0.5">!</span>
                      <span>{limitation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* New platform highlight */}
      <Card className="bg-gradient-to-br from-primary/20 to-secondary/20 border-2 border-primary">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl flex items-center gap-2">
                <Icon name="Sparkles" className="text-primary" size={28} />
                {newPlatform.name}
              </CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                Автономный ИИ-агент нового поколения
              </p>
            </div>
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center text-white font-bold text-3xl shadow-lg">
              {newPlatform.score}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Key features */}
          <div>
            <div className="text-sm font-semibold mb-3 flex items-center gap-2">
              <Icon name="Check" className="text-green-500" size={18} />
              Ключевые преимущества:
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {newPlatform.features.map((feature, idx) => (
                <div key={idx} className="flex items-start gap-2 text-sm">
                  <Icon name="CheckCircle2" size={16} className="text-green-500 mt-0.5 flex-shrink-0" />
                  <span>{feature}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Metrics comparison */}
          <div>
            <div className="text-sm font-semibold mb-3 flex items-center gap-2">
              <Icon name="BarChart3" className="text-primary" size={18} />
              Метрики vs конкуренты:
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {newPlatform.metrics.map((metric, idx) => (
                <div key={idx} className="bg-background/50 p-3 rounded-lg border">
                  <div className="flex items-center gap-2 mb-1">
                    <Icon name={metric.icon} size={16} className="text-primary" />
                    <div className="text-xs text-muted-foreground">{metric.label}</div>
                  </div>
                  <div className="font-bold text-lg text-primary">{metric.value}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Call to action */}
          <div className="bg-primary/10 p-4 rounded-lg text-center">
            <div className="text-lg font-semibold mb-1">Время до продакшена</div>
            <div className="text-4xl font-bold text-primary mb-2">&lt;10 минут</div>
            <div className="text-sm text-muted-foreground">
              против 2-8 часов ручной работы у конкурентов
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PlatformComparison;
