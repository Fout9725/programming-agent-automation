import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';

interface WorkflowStep {
  id: number;
  title: string;
  description: string;
  icon: string;
  duration: string;
  output?: string;
  metrics?: { label: string; value: string }[];
}

const ExampleWorkflow = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const workflowSteps: WorkflowStep[] = [
    {
      id: 0,
      title: 'Запрос пользователя',
      description: '"Создай интернет-магазин с корзиной и оплатой"',
      icon: 'MessageSquare',
      duration: '0 сек',
      output: 'Запрос принят в обработку'
    },
    {
      id: 1,
      title: 'Интерпретация запроса',
      description: 'GPT-5.2 анализирует требования и создает техспецификацию',
      icon: 'Brain',
      duration: '3 сек',
      output: `{
  "frontend": "React + TypeScript + shadcn/ui",
  "pages": ["ProductList", "ProductDetail", "Cart", "Checkout"],
  "backend": "Python FastAPI",
  "endpoints": ["/api/products", "/api/cart", "/api/orders"],
  "database": "PostgreSQL",
  "integrations": ["Stripe API"]
}`,
      metrics: [
        { label: 'Страниц', value: '4' },
        { label: 'API endpoints', value: '5' },
        { label: 'Таблиц БД', value: '5' }
      ]
    },
    {
      id: 2,
      title: 'Генерация кода',
      description: 'Ансамбль моделей создает frontend, backend и БД схему',
      icon: 'Code',
      duration: '45 сек',
      output: `✓ Frontend: 23 файла (React components, pages, hooks)
✓ Backend: 8 файлов (FastAPI endpoints, models)
✓ Database: 5 таблиц с индексами
✓ Tests: 42 теста (unit + integration)`,
      metrics: [
        { label: 'Файлов', value: '47' },
        { label: 'Строк кода', value: '3,842' },
        { label: 'Тестов', value: '42' }
      ]
    },
    {
      id: 3,
      title: 'Валидация и автофикс',
      description: 'Проверка качества кода и безопасности',
      icon: 'Shield',
      duration: '12 сек',
      output: `✓ ESLint: 0 ошибок
✓ TypeScript: strict mode passed
✓ Semgrep security: 0 критических уязвимостей
✓ Автофикс: 3 предупреждения исправлены`,
      metrics: [
        { label: 'Code Quality', value: 'A' },
        { label: 'Security Score', value: '100' },
        { label: 'Автофиксы', value: '3' }
      ]
    },
    {
      id: 4,
      title: 'Автономное тестирование',
      description: 'Запуск всех тестов и автофикс при падении',
      icon: 'CheckCircle',
      duration: '25 сек',
      output: `✓ Unit tests: 28/28 passed
✓ Integration tests: 10/10 passed
✓ E2E tests: 4/4 passed
✓ Coverage: 94%`,
      metrics: [
        { label: 'Pass rate', value: '100%' },
        { label: 'Coverage', value: '94%' },
        { label: 'Итераций', value: '1' }
      ]
    },
    {
      id: 5,
      title: 'Деплой в продакшен',
      description: 'GitHub commit, Terraform, SSL, CDN',
      icon: 'Rocket',
      duration: '75 сек',
      output: `✓ GitHub: commit + PR + auto-merge
✓ Terraform: AWS Lambda + RDS + CloudFront
✓ SSL certificate: auto-provisioned
✓ Monitoring: Sentry + CloudWatch`,
      metrics: [
        { label: 'Frontend', value: 'my-shop.com' },
        { label: 'Backend', value: 'api.my-shop.com' },
        { label: 'Lighthouse', value: '96/100' }
      ]
    },
    {
      id: 6,
      title: 'Готово!',
      description: 'Проект развернут и доступен пользователям',
      icon: 'PartyPopper',
      duration: '2 мин 40 сек',
      output: `🎉 Deployment complete!

Frontend: https://my-shop.com
Backend: https://api.my-shop.com
GitHub: https://github.com/user/my-shop
Admin: https://my-shop.com/admin

Cost: $23/month (estimated for 10K visitors)`,
      metrics: [
        { label: 'Общее время', value: '2m 40s' },
        { label: 'Стоимость', value: '$23/мес' },
        { label: 'Performance', value: '96/100' }
      ]
    }
  ];

  useEffect(() => {
    if (isPlaying && currentStep < workflowSteps.length - 1) {
      const timer = setTimeout(() => {
        setCurrentStep((prev) => prev + 1);
      }, 2000);
      return () => clearTimeout(timer);
    } else if (currentStep >= workflowSteps.length - 1) {
      setIsPlaying(false);
    }
  }, [isPlaying, currentStep, workflowSteps.length]);

  const handlePlay = () => {
    if (currentStep >= workflowSteps.length - 1) {
      setCurrentStep(0);
    }
    setIsPlaying(true);
  };

  const handlePause = () => {
    setIsPlaying(false);
  };

  const handleReset = () => {
    setCurrentStep(0);
    setIsPlaying(false);
  };

  const currentWorkflowStep = workflowSteps[currentStep];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold mb-2">Пример работы агента</h2>
        <p className="text-muted-foreground">
          От запроса до готового интернет-магазина за 2 минуты 40 секунд
        </p>
      </div>

      {/* Controls */}
      <div className="flex justify-center gap-3">
        {!isPlaying ? (
          <Button onClick={handlePlay} size="lg">
            <Icon name="Play" className="mr-2" size={18} />
            {currentStep === 0 ? 'Запустить демо' : 'Продолжить'}
          </Button>
        ) : (
          <Button onClick={handlePause} size="lg" variant="outline">
            <Icon name="Pause" className="mr-2" size={18} />
            Пауза
          </Button>
        )}
        <Button onClick={handleReset} size="lg" variant="outline">
          <Icon name="RotateCcw" className="mr-2" size={18} />
          Сброс
        </Button>
      </div>

      {/* Progress bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>Шаг {currentStep + 1} из {workflowSteps.length}</span>
          <span>{currentWorkflowStep.duration}</span>
        </div>
        <div className="w-full bg-secondary rounded-full h-2">
          <div
            className="bg-primary h-2 rounded-full transition-all duration-500"
            style={{ width: `${((currentStep + 1) / workflowSteps.length) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Current step display */}
      <Card className="border-2 border-primary">
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center">
              <Icon name={currentWorkflowStep.icon} className="text-white" size={28} />
            </div>
            <div className="flex-1">
              <CardTitle className="text-2xl">{currentWorkflowStep.title}</CardTitle>
              <p className="text-muted-foreground mt-1">{currentWorkflowStep.description}</p>
            </div>
            <Badge className="text-lg px-4 py-2">{currentWorkflowStep.duration}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {currentWorkflowStep.output && (
            <div className="bg-muted p-4 rounded-lg font-mono text-sm whitespace-pre-wrap">
              {currentWorkflowStep.output}
            </div>
          )}

          {currentWorkflowStep.metrics && (
            <div className="grid grid-cols-3 gap-4">
              {currentWorkflowStep.metrics.map((metric, idx) => (
                <div key={idx} className="bg-background p-3 rounded-lg border text-center">
                  <div className="text-sm text-muted-foreground mb-1">{metric.label}</div>
                  <div className="text-2xl font-bold text-primary">{metric.value}</div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Timeline */}
      <div className="relative">
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-border"></div>
        <div className="space-y-4">
          {workflowSteps.map((step, index) => (
            <div
              key={step.id}
              className={`flex items-start gap-4 transition-all duration-300 ${
                index <= currentStep ? 'opacity-100' : 'opacity-30'
              }`}
            >
              <div
                className={`relative z-10 w-16 h-16 rounded-full flex items-center justify-center border-4 transition-colors ${
                  index === currentStep
                    ? 'bg-primary border-primary text-white scale-110'
                    : index < currentStep
                    ? 'bg-green-500 border-green-500 text-white'
                    : 'bg-background border-border'
                }`}
              >
                {index < currentStep ? (
                  <Icon name="Check" size={24} />
                ) : (
                  <Icon name={step.icon} size={24} />
                )}
              </div>
              <div className="flex-1 pt-2">
                <div className="text-sm font-semibold">{step.title}</div>
                <div className="text-xs text-muted-foreground">{step.duration}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ExampleWorkflow;
