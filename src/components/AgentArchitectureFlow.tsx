import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';

interface FlowNode {
  id: string;
  title: string;
  icon: string;
  description: string;
  color: string;
  metrics?: { label: string; value: string }[];
  details?: string[];
}

const AgentArchitectureFlow = () => {
  const [activeNode, setActiveNode] = useState<string | null>(null);

  const flowNodes: FlowNode[] = [
    {
      id: 'input',
      title: 'Текстовый запрос',
      icon: 'MessageSquare',
      description: 'Пользователь описывает проект на естественном языке',
      color: 'bg-blue-500',
      details: [
        'Поддержка русского и английского',
        'Распознавание голоса (Whisper)',
        'Анализ скриншотов дизайна (GPT-4V)',
        'Figma → React конвертер'
      ]
    },
    {
      id: 'interpreter',
      title: 'Мультимодальный интерпретатор',
      icon: 'Brain',
      description: 'Разбор запроса в техническую спецификацию',
      color: 'bg-purple-500',
      metrics: [
        { label: 'Модель', value: 'GPT-5.2 Chat' },
        { label: 'Точность', value: '94%' }
      ],
      details: [
        'NLU Parser (понимание контекста)',
        'Decomposer (разбивка на задачи)',
        'Conflict Detector (поиск противоречий)',
        'Clarification Agent (уточнение требований)'
      ]
    },
    {
      id: 'generator',
      title: 'Генератор кода',
      icon: 'Code',
      description: 'Создание frontend, backend, database',
      color: 'bg-green-500',
      metrics: [
        { label: 'Frontend', value: 'GPT-5.1 Codex' },
        { label: 'Backend', value: 'Claude Opus 4.5' },
        { label: 'Database', value: 'O3 Deep Research' }
      ],
      details: [
        'React + TypeScript (строгая типизация)',
        'Python FastAPI / Node.js (бэкенд)',
        'PostgreSQL схемы с индексами',
        'Модульная архитектура (до 50 файлов)'
      ]
    },
    {
      id: 'validator',
      title: 'Валидатор + Автофикс',
      icon: 'Shield',
      description: 'Проверка качества и безопасности',
      color: 'bg-orange-500',
      metrics: [
        { label: 'Code Quality', value: 'A (SonarQube)' },
        { label: 'Security', value: '0 критических' }
      ],
      details: [
        'ESLint + TypeScript strict',
        'Pylint + Bandit (Python)',
        'Semgrep (security patterns)',
        'Автофикс до 10 итераций'
      ]
    },
    {
      id: 'testing',
      title: 'Автономное тестирование',
      icon: 'CheckCircle',
      description: 'Генерация и запуск тестов',
      color: 'bg-cyan-500',
      metrics: [
        { label: 'Coverage', value: '>85%' },
        { label: 'Pass rate', value: '100%' }
      ],
      details: [
        'Unit tests (Jest / Pytest)',
        'Integration tests (Playwright)',
        'E2E tests (Cypress)',
        'Auto-fix до прохождения всех тестов'
      ]
    },
    {
      id: 'deployment',
      title: 'Автономный деплой',
      icon: 'Rocket',
      description: 'Публикация в облако',
      color: 'bg-pink-500',
      metrics: [
        { label: 'Time', value: '<3 мин' },
        { label: 'Success', value: '>95%' }
      ],
      details: [
        'GitHub: auto commit/PR/merge',
        'Terraform: AWS/GCP/Azure',
        'SSL + CDN автоматически',
        'Мониторинг (Sentry + LogRocket)'
      ]
    }
  ];

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold mb-2">Архитектура автономного агента</h2>
        <p className="text-muted-foreground">
          От текстового запроса до готового продукта за 10 минут
        </p>
      </div>

      <div className="relative">
        {/* Flow diagram */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {flowNodes.map((node, index) => (
            <div key={node.id} className="relative">
              <Card
                className={`cursor-pointer transition-all duration-300 hover:scale-105 ${
                  activeNode === node.id ? 'ring-2 ring-primary shadow-2xl' : ''
                }`}
                onClick={() => setActiveNode(activeNode === node.id ? null : node.id)}
              >
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-lg ${node.color} flex items-center justify-center`}>
                      <Icon name={node.icon} className="text-white" size={24} />
                    </div>
                    <div className="flex-1">
                      <CardTitle className="text-lg">{node.title}</CardTitle>
                      <Badge variant="outline" className="mt-1 text-xs">
                        Шаг {index + 1}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-muted-foreground">{node.description}</p>
                  
                  {node.metrics && (
                    <div className="grid grid-cols-2 gap-2">
                      {node.metrics.map((metric, idx) => (
                        <div key={idx} className="bg-muted p-2 rounded">
                          <div className="text-xs text-muted-foreground">{metric.label}</div>
                          <div className="font-semibold text-sm">{metric.value}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {activeNode === node.id && node.details && (
                    <div className="mt-4 space-y-2 animate-fade-in">
                      {node.details.map((detail, idx) => (
                        <div key={idx} className="flex items-start gap-2 text-xs">
                          <Icon name="CheckCircle2" size={14} className="text-green-500 mt-0.5 flex-shrink-0" />
                          <span>{detail}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Arrow connector */}
              {index < flowNodes.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-3 transform -translate-y-1/2 z-10">
                  <Icon name="ArrowRight" className="text-muted-foreground" size={24} />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Visual connections for mobile */}
        <div className="lg:hidden flex justify-center gap-2 mt-4">
          {flowNodes.map((_, index) => (
            <div key={index} className="flex items-center">
              <div className="w-2 h-2 rounded-full bg-primary"></div>
              {index < flowNodes.length - 1 && (
                <div className="w-8 h-0.5 bg-primary"></div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Key metrics */}
      <Card className="bg-gradient-to-br from-primary/10 to-secondary/10">
        <CardContent className="pt-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">&lt;10 мин</div>
              <div className="text-xs text-muted-foreground mt-1">Time to Production</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-500">A</div>
              <div className="text-xs text-muted-foreground mt-1">Code Quality</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-cyan-500">100%</div>
              <div className="text-xs text-muted-foreground mt-1">Test Pass Rate</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-500">0</div>
              <div className="text-xs text-muted-foreground mt-1">Critical Issues</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AgentArchitectureFlow;
