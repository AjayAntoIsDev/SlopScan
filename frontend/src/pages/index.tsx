import { Input } from "@heroui/input";
import { Button } from "@heroui/button";
import { Accordion, AccordionItem } from "@heroui/accordion";
import { Settings, HelpCircle } from "lucide-react";
import { Select, SelectItem } from "@heroui/select";
import { NumberInput } from "@heroui/number-input";
import { Tooltip } from "@heroui/tooltip";
import { useState } from "react";

import { SearchIcon } from "@/components/icons";
import { title, subtitle } from "@/components/primitives";
import { RepoAnalysis } from "@/components/repo-analysis";
import { CodeAnalysis } from "@/components/code-analysis";
import { LoadingModal } from "@/components/loading-modal";
import {
  analysisService,
  type AnalysisResult,
} from "@/services/analysis-service";
import DefaultLayout from "@/layouts/default";

export default function IndexPage() {
  const [fullyLoaded, setIsFullyLoaded] = useState(false);
  const [finalSlopScore, setFinalSlopScore] = useState(0);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingStatus, setLoadingStatus] = useState("");
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null,
  );
  const [analysisMode, setAnalysisMode] = useState<"both" | "repo" | "code">(
    "both",
  );
  const [maxFiles, setMaxFiles] = useState(50);
  const [isValidUrl, setIsValidUrl] = useState(false);

  const validateUrl = (value: string) => {
    if (!value) {
      return "";
    }

    const githubPattern = /^https:\/\/github\.com\/[\w\-\.]+\/[\w\-\.]+$/;
    const somPattern = /^https:\/\/summer\.hackclub\.com\/projects\/\d+$/;

    if (!githubPattern.test(value) && !somPattern.test(value)) {
      return "Must be a valid GitHub repo link or SoM project link";
    }

    return null;
  };

  const handleInputChange = (value: string) => {
    setInputValue(value);
    const validation = validateUrl(value);

    setIsValidUrl(validation === null && value.trim() !== "");
  };

  const handleSubmit = async () => {
    const validation = validateUrl(inputValue);

    if (validation === null && inputValue.trim()) {
      setIsModalOpen(true);
      setLoadingProgress(0);
      setLoadingStatus("Initializing analysis...");

      try {
        const result = await analysisService.mockAnalyzeRepository(
          inputValue,
          {
            mode: analysisMode,
            maxFiles: maxFiles,
          },
          (progress, status) => {
            setLoadingProgress(progress);
            setLoadingStatus(status);
          },
        );

        setAnalysisResult(result);
        setFinalSlopScore(result.overallSlopScore);
        setIsFullyLoaded(true);
        setIsModalOpen(false);
      } catch (error) {
        console.error("Analysis failed:", error);
        setLoadingStatus("Analysis failed. Please try again.");
        setLoadingProgress(0);

        setTimeout(() => {
          setIsModalOpen(false);
        }, 2000);
      }
    }
  };

  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <div className="inline-block max-w-lg text-center justify-center">
          <span className={title()}>Detect&nbsp;</span>
          <span className={title({ color: "blue" })}>Slop&nbsp;</span>
          <span className={title()}>with ease.</span>
          <div className={subtitle({ class: "mt-4" })}>
            AI powered slop detection tool that actually works
          </div>
        </div>

        <div className="w-3/6 mt-4 flex flex-col gap-4">
          <div className="flex gap-3 w-full">
            <Input
              isRequired
              labelPlacement="outside"
              name="repoUrl"
              placeholder="Enter GitHub repo or SoM project URL"
              type="url"
              validate={validateUrl}
              value={inputValue}
              onValueChange={handleInputChange}
            />
            <Button
              color="primary"
              isDisabled={!isValidUrl || isModalOpen}
              type="submit"
              onPress={handleSubmit}
            >
              <SearchIcon className="h-5 w-5" />
            </Button>
          </div>
          <Accordion variant="splitted">
            <AccordionItem
              key="1"
              aria-label="Accordion 1"
              classNames=""
              indicator={<Settings />}
              title="Advanced Settings"
            >
              <div className="flex flex-col gap-6 p-2">
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Select
                      className="flex-1"
                      defaultSelectedKeys={["both"]}
                      label="Analysis Mode"
                      size="sm"
                      variant="bordered"
                      onSelectionChange={(selection) => {
                        const value = Array.from(selection)[0] as
                          | "both"
                          | "repo"
                          | "code";

                        setAnalysisMode(value);
                      }}
                    >
                      <SelectItem key={"both"}>
                        Repo Analysis + Code Analysis
                      </SelectItem>
                      <SelectItem key={"repo"}>Repo Analysis</SelectItem>
                      <SelectItem key={"code"}>Code Analysis</SelectItem>
                    </Select>
                    <Tooltip
                      content="Choose the type of analysis to perform"
                      placement="top"
                    >
                      <HelpCircle className="h-4 w-4 text-gray-500 cursor-help  transition-colors" />
                    </Tooltip>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <NumberInput
                      className="flex-1"
                      defaultValue={50}
                      isDisabled={true}
                      label="Max files to analyze"
                      max={100}
                      min={1}
                      size="sm"
                      step={10}
                      value={maxFiles}
                      variant="bordered"
                      onValueChange={(value) => setMaxFiles(value as number)}
                    />
                    <Tooltip
                      content="Limit the number of files to analyze to control processing time (Disabled coz i am too broke to pay for more 😭)"
                      placement="top"
                    >
                      <HelpCircle className="h-4 w-4 text-gray-500 cursor-help  transition-colors" />
                    </Tooltip>
                  </div>
                </div>
              </div>
            </AccordionItem>
          </Accordion>
        </div>
        <div className="mt-4 w-full max-w-6xl mx-auto">
          <div className="mb-6 flex justify-center">
            <div className="text-center">
              <div className="text-5xl font-bold text-danger">
                {!fullyLoaded ? "?" : finalSlopScore}
                <span className="text-sm text-default-600">/100</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <RepoAnalysis blurred={!fullyLoaded} data={analysisResult} />
            <CodeAnalysis blurred={!fullyLoaded} data={analysisResult} />
          </div>
        </div>

        <LoadingModal
          isOpen={isModalOpen}
          progress={loadingProgress}
          status={loadingStatus}
          url={inputValue}
          onClose={() => setIsModalOpen(false)}
        />
      </section>
    </DefaultLayout>
  );
}
