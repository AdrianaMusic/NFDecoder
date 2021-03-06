#!/usr/bin/env python
'''
 * Copyright (c) 2018 Spotify AB.
 *
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 '''

import os
import sys

from nfbuildosx import NFBuildOSX
from build_options import BuildOptions


def main():
    buildOptions = BuildOptions()
    buildOptions.addOption("debug", "Enable Debug Mode")

    buildOptions.addOption("lintCmake", "Lint cmake files")
    buildOptions.addOption("lintCpp", "Lint CPP Files")
    buildOptions.addOption("lintCppWithInlineChange",
                           "Lint CPP Files and fix them")

    buildOptions.addOption("integrationTests", "Run Integration Tests")

    buildOptions.addOption("makeBuildDirectory",
                           "Wipe existing build directory")
    buildOptions.addOption("generateProject", "Regenerate xcode project")

    buildOptions.addOption("addressSanitizer",
                           "Enable Address Sanitizer in generate project")
    buildOptions.addOption("ubSanitizer",
                           "Enable UB Sanitizer in generate project")
    buildOptions.addOption("codeCoverage",
                           "Enable code coverage in generate project")
    buildOptions.addOption("ffmpeg", "Use ffmpeg for decode")

    buildOptions.addOption("printStackTrace",
                           "Enable print stack trace")

    buildOptions.addOption("buildTargetCLI", "Build Target: CLI")
    buildOptions.addOption("buildTargetLibrary", "Build Target: Library")

    buildOptions.addOption("staticAnalysis", "Run Static Analysis")

    buildOptions.setDefaultWorkflow("Empty workflow", [])

    buildOptions.addWorkflow("local_it", "Run local integration tests", [
        'debug',
        'lintCmake',
        'integrationTests'
    ])

    buildOptions.addWorkflow("lint", "Run lint workflow", [
        'lintCmake',
        'lintCppWithInlineChange'
    ])

    buildOptions.addWorkflow("address_sanitizer", "Run address sanitizer", [
        'lintCmake',
        'lintCpp',
        'makeBuildDirectory',
        'generateProject',
        'addressSanitizer',
        'buildTargetCLI',
        'integrationTests'
    ])

    buildOptions.addWorkflow("ub_sanitizer", "Run UB sanitizer", [
        'printStackTrace',
        'lintCmake',
        'lintCpp',
        'makeBuildDirectory',
        'generateProject',
        'ubSanitizer',
        'buildTargetCLI',
        'integrationTests'
    ])


    buildOptions.addWorkflow("code_coverage", "Collect code coverage", [
        'debug',
        'lintCmake',
        'lintCpp',
        'makeBuildDirectory',
        'generateProject',
        'codeCoverage',
        'buildTargetCLI',
        'integrationTests'
    ])

    buildOptions.addWorkflow("build", "Production Build", [
        'lintCmake',
        'lintCpp',
        'makeBuildDirectory',
        'generateProject',
        'buildTargetCLI',
        'buildTargetLibrary',
        'staticAnalysis',
        'integrationTests'
    ])

    options = buildOptions.parseArgs()

    buildOptions.verbosePrintBuildOptions(options)


    library_target = 'NFDecoder'
    cli_target = 'NFDecoderCLI'
    nfbuild = NFBuildOSX()

    if buildOptions.checkOption(options, 'debug'):
        nfbuild.build_type = 'Debug'

    if buildOptions.checkOption(options, 'lintCmake'):
        nfbuild.lintCmake()

    if buildOptions.checkOption(options, 'lintCppWithInlineChange'):
        nfbuild.lintCPP(make_inline_changes=True)
    elif buildOptions.checkOption(options, 'lintCpp'):
        nfbuild.lintCPP(make_inline_changes=False)

    if buildOptions.checkOption(options, 'makeBuildDirectory'):
        nfbuild.makeBuildDirectory()

    if buildOptions.checkOption(options, 'printStackTrace'):
        os.environ['UBSAN_OPTIONS'] = 'print_stacktrace=1'

    if buildOptions.checkOption(options, 'generateProject'):
        nfbuild.generateProject(
            code_coverage='codeCoverage' in options,
            address_sanitizer='addressSanitizer' in options,
            ub_sanitizer='ubSanitizer' in options,
            use_ffmpeg='ffmpeg' in options
            )

    if buildOptions.checkOption(options, 'buildTargetLibrary'):
        nfbuild.buildTarget(library_target)
        if buildOptions.checkOption(options, 'staticAnalysis'):
            nfbuild.staticallyAnalyse(library_target,
                                      include_regex='source/.*')

    if buildOptions.checkOption(options, 'buildTargetCLI'):
        nfbuild.buildTarget(cli_target)
        if buildOptions.checkOption(options, 'staticAnalysis'):
            nfbuild.staticallyAnalyse(cli_target,
                                      include_regex='source/.*')

    if buildOptions.checkOption(options, 'integrationTests'):
        nfbuild.runIntegrationTests()

    if buildOptions.checkOption(options, 'codeCoverage'):
        nfbuild.collectCodeCoverage()


if __name__ == "__main__":
    main()
