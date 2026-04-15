import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';

interface BuildStep {
  key: string;
  label: string;
  status: 'completed' | 'in_progress' | 'pending';
  duration_ms?: number;
}

interface BuildProgressProps {
  steps: BuildStep[];
  progress: number;
  currentStep: string;
}

const STEP_ICONS: Record<string, string> = {
  analyzing: 'Brain',
  generating_db: 'Database',
  generating_backend: 'Server',
  generating_frontend: 'Layout',
  validating: 'ShieldCheck',
  deploying: 'Rocket',
};

const BuildProgress = ({ steps, progress, currentStep }: BuildProgressProps) => {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-2">
            <span className="font-medium">{currentStep}</span>
            <span className="text-muted-foreground">{Math.round(progress * 100)}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-500"
              style={{ width: `${progress * 100}%` }}
            />
          </div>
        </div>

        <div className="space-y-3">
          {steps.map((step) => (
            <div key={step.key} className="flex items-center gap-3">
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                step.status === 'completed' ? 'bg-green-100 dark:bg-green-900' :
                step.status === 'in_progress' ? 'bg-primary/10' :
                'bg-muted'
              }`}>
                {step.status === 'completed' ? (
                  <Icon name="Check" size={16} className="text-green-600 dark:text-green-400" />
                ) : step.status === 'in_progress' ? (
                  <Icon name="Loader2" size={16} className="text-primary animate-spin" />
                ) : (
                  <Icon name={STEP_ICONS[step.key] || 'Circle'} size={16} className="text-muted-foreground" />
                )}
              </div>
              <div className="flex-1">
                <span className={`text-sm ${
                  step.status === 'completed' ? 'text-green-600 dark:text-green-400' :
                  step.status === 'in_progress' ? 'text-foreground font-medium' :
                  'text-muted-foreground'
                }`}>
                  {step.label}
                </span>
              </div>
              {step.status === 'completed' && step.duration_ms && (
                <Badge variant="secondary" className="text-xs">
                  {(step.duration_ms / 1000).toFixed(1)}c
                </Badge>
              )}
              {step.status === 'in_progress' && (
                <Badge variant="default" className="text-xs animate-pulse">
                  ...
                </Badge>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default BuildProgress;
