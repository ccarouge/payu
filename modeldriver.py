# coding: utf-8

import os
import shutil

from fsops import mkdir_p

# TODO: Redesign the various models to subclass Model
class Model(object):

    def __init__(self, expt, model_name, model_config):

        # Inherit experiment configuration
        self.expt = expt
        self.name = model_name
        self.config = model_config

        #---
        # Null stuff, mostly to remind me what needs configuring in the drivers

        # Model details
        self.model_type = None
        self.default_exec = None
        self.input_basepath = None

        # Path names
        self.work_input_path = None
        self.work_restart_path = None
        self.exec_path = None


    #---
    def set_model_pathnames(self):

        self.control_path = self.expt.control_path
        self.input_basepath = self.expt.input_basepath
        self.work_path = self.expt.work_path

        if len(self.expt.models) > 1:

            self.control_path = os.path.join(self.control_path, self.name)
            self.work_path = os.path.join(self.work_path, self.name)

        # NOTE: Individual models may override the work subdirectories
        self.work_input_path = self.work_path
        self.work_restart_path = self.work_path

        assert self.default_exec
        exec_name = self.expt.config.get('exe', self.default_exec)
        self.exec_path = os.path.join(self.expt.bin_path, exec_name)


    #---
    def set_input_paths(self):

        if len(self.expt.models) == 1:
            input_dirs = self.expt.config.get('input')
        else:
            input_dirs = self.config.get('input')

        if input_dirs is None:
            input_dirs = []
        elif type(input_dirs) == str:
            input_dirs = [input_dirs]

        self.input_paths = []
        for input_dir in input_dirs:

            # First test for absolute path
            if os.path.exists(input_dir):
                self.input_paths.append(input_dir)
            else:
                # Test for path relative to /${lab_path}/input/${model_name}
                assert self.input_basepath
                rel_path = os.path.join(self.input_basepath, input_dir)
                if os.path.exists(rel_path):
                    self.input_paths.append(rel_path)
                else:
                    sys.exit('payu: error: Input directory {} not found; '
                             'aborting.'.format(rel_path))


    #---
    def set_output_paths(self):
        # NYI
        pass


    #---
    def setup(self):

        mkdir_p(self.work_path)

        # Copy configuration files from control path
        for f in self.config_files:
            f_path = os.path.join(self.control_path, f)
            shutil.copy(f_path, self.work_path)