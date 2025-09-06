import type { AnalysisResult } from "@/services/analysis-service";

import { Card, CardHeader, CardBody } from "@heroui/card";
import { Chip } from "@heroui/chip";
import { ScrollShadow } from "@heroui/scroll-shadow";
import { Brain, Code, Target, Zap, Copy } from "lucide-react";

interface CodeAnalysisProps {
  blurred?: boolean;
  data?: AnalysisResult | null;
}

export function CodeAnalysis({ blurred = false, data }: CodeAnalysisProps) {
  const codeData = data?.codeAnalysis || {
    aiInCode: 0,
    perfectness: 0,
    unusedCode: 0,
  };

  const code_analysis = data?.code_analysis.analysis.ai_analysis || {};

  return (
    <div className="w-full">
      <Card
        className={`w-full h-full flex ${blurred ? "blur-lg" : ""} ${!data?.code_analysis?.enabled ? "blur-lg" : ""}`}
        radius="lg"
      >
        <CardBody className="pt-2">
          <div className="flex flex-col gap-4 justify-center items-center h-full">
            <div className="flex flex-col gap-4 w-full">
              <Card className="col-span-2 row-span-1 pb-2" radius="lg">
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2">
                    <Code className="h-5 w-5 text-secondary" />
                    <h3 className="text-lg font-bold">Code Analysis</h3>
                  </div>
                </CardHeader>

                <CardBody>
                  <div className="grid grid-cols-3 gap-4 w-full">
                    <div className="text-center">
                      <Brain className="h-6 w-6 text-primary mx-auto mb-2" />
                      <div className="text-2xl font-bold text-primary">
                        {Math.round(code_analysis.analysis_results.ai)}%
                      </div>
                      <div className="text-sm text-default-600">AI in code</div>
                    </div>
                    <div className="text-center">
                      <Zap className="h-6 w-6 text-secondary mx-auto mb-2" />
                      <div className="text-2xl font-bold text-secondary">
                        {Math.round(code_analysis.analysis_results.perfectness)}
                        %
                      </div>
                      <div className="text-sm text-default-600">
                        Perfectness
                      </div>
                    </div>
                    <div className="text-center">
                      <Copy className="h-6 w-6 text-warning mx-auto mb-2" />
                      <div className="text-2xl font-bold text-warning">
                        {Math.round(code_analysis.analysis_results.unused)}%
                      </div>
                      <div className="text-sm text-default-600">
                        Unused Code
                      </div>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </div>
            <div className="col-span-2 row-span-1 flex flex-col gap-4">
              <Card className="pb-2 h-full" radius="lg">
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2">
                    <Target className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-bold">SlopScore</h3>
                  </div>
                </CardHeader>

                <CardBody className="grid grid-cols-4 grid-rows-1 gap-4">
                  <div className="text-center flex items-center justify-center">
                    <div className="text-5xl font-bold text-primary">
                      {code_analysis.analysis_results.ai}
                      <span className="text-xs text-default-600">/100</span>
                    </div>
                  </div>
                  <div className="col-span-3">
                    <ScrollShadow className="h-32 p-3 bg-default-50 rounded-lg">
                      <div className="space-y-2 text-xs">
                        {code_analysis.analysis_results.reasoning}
                      </div>
                    </ScrollShadow>
                  </div>
                </CardBody>
              </Card>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
