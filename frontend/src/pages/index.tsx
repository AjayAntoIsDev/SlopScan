import { Input } from "@heroui/input";
import { Button } from "@heroui/button";
import { Accordion, AccordionItem } from "@heroui/accordion";
import { Settings, Brain, Code, HelpCircle } from "lucide-react";
import { Switch } from "@heroui/switch";
import { Select, SelectItem } from "@heroui/select";
import { NumberInput } from "@heroui/number-input";
import { Tooltip } from "@heroui/tooltip";

import { SearchIcon } from "@/components/icons";
import { title, subtitle } from "@/components/primitives";
import DefaultLayout from "@/layouts/default";

export default function IndexPage() {
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
              validate={(value) => {
                if (!value) {
                  return "URL is required";
                }

                const githubPattern =
                  /^https:\/\/github\.com\/[\w\-\.]+\/[\w\-\.]+$/;
                const somPattern =
                  /^https:\/\/summer\.hackclub\.com\/projects\/\d+$/;

                if (!githubPattern.test(value) && !somPattern.test(value)) {
                  return "Must be a valid GitHub repo link or SoM project link";
                }

                return null;
              }}
            />
            <Button color="primary" type="submit">
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
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Switch
                        defaultSelected
                        color="primary"
                        endContent={<Code />}
                        size="lg"
                        startContent={<Brain />}
                      >
                        Enable AI Analysis
                      </Switch>
                    </div>
                    <Tooltip
                      content="Use AI for slop detection"
                      placement="top"
                    >
                      <HelpCircle className="h-4 w-4 text-gray-500 cursor-help  transition-colors" />
                    </Tooltip>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Select
                      className="flex-1"
                      defaultSelectedKeys={["both"]}
                      label="Analysis Mode"
                      size="sm"
                      variant="bordered"
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
                      variant="bordered"
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
      </section>
    </DefaultLayout>
  );
}
