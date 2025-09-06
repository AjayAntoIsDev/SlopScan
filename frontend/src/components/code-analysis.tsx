import { Card, CardHeader, CardBody } from "@heroui/card";
import { Chip } from "@heroui/chip";
import { ScrollShadow } from "@heroui/scroll-shadow";
import { Brain, Code, Target, Zap, Copy } from "lucide-react";

interface CodeAnalysisProps {
  blurred?: boolean;
}

export function CodeAnalysis({ blurred = false }: CodeAnalysisProps) {
  return (
    <div className="w-full">
      <Card
        className={`w-full h-full flex ${blurred ? "blur-lg" : ""}`}
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
                      <div className="text-2xl font-bold text-primary">8.2</div>
                      <div className="text-sm text-default-600">AI in code</div>
                    </div>
                    <div className="text-center">
                      <Zap className="h-6 w-6 text-secondary mx-auto mb-2" />
                      <div className="text-2xl font-bold text-secondary">
                        94%
                      </div>
                      <div className="text-sm text-default-600">
                        Perfectness
                      </div>
                    </div>
                    <div className="text-center">
                      <Copy className="h-6 w-6 text-warning mx-auto mb-2" />
                      <div className="text-2xl font-bold text-warning">23%</div>
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
                      85
                      <span className="text-xs text-default-600">/100</span>
                    </div>
                  </div>
                  <div className="flex flex-col gap-1 justify-center">
                    <Chip
                      className="text-xs px-2 py-0.5 h-5"
                      color="primary"
                      size="sm"
                      variant="flat"
                    >
                      Clean structure
                    </Chip>
                    <Chip
                      className="text-xs px-2 py-0.5 h-5"
                      color="warning"
                      size="sm"
                      variant="flat"
                    >
                      Some duplicates
                    </Chip>
                    <Chip
                      className="text-xs px-2 py-0.5 h-5"
                      color="secondary"
                      size="sm"
                      variant="flat"
                    >
                      Good performance
                    </Chip>
                  </div>
                  <div className="col-span-2">
                    <ScrollShadow className="h-32 p-3 bg-default-50 rounded-lg">
                      <div className="space-y-2 text-xs">
                        Lorem ipsum dolor sit amet, consectetur adipisicing
                        elit. Excepturi architecto pariatur maxime expedita
                        ullam aliquid recusandae iste minima qui, ducimus
                        dolorem sunt culpa? Ad rerum beatae repellendus
                        laboriosam officiis. Ab. Lorem ipsum dolor sit amet
                        consectetur adipisicing elit. Non ipsum eaque architecto
                        nobis voluptates dolorem commodi quidem. Asperiores
                        harum culpa nesciunt magnam eos impedit fugit. Rerum sit
                        expedita consequatur aperiam.
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
