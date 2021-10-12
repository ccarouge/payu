"""payu.models.cable
   ================

   Driver interface to CABLE

   :copyright: Copyright 2021 Marshall Ward, see AUTHORS for details
   :license: Apache License, Version 2.0, see LICENSE for details
"""

# Standard Library
import os
import shutil

# Extensions
import f90nml

# Local
from payu.fsops import mkdir_p
from payu.models.model import Model


class Cable(Model):

    def __init__(self, expt, name, config):
        super(Cable, self).__init__(expt, name, config)

        self.model_type = 'cable'
        self.default_exec = 'cable'

        self.cable_nml_fname = 'cable.nml'

        self.config_files = [
            self.cable_nml_fname,
        ]

    def set_model_pathnames(self):
        super(Cable, self).set_model_pathnames()

        self.cable_nml = f90nml.read(
            os.path.join(self.control_path, self.cable_nml_fname)
        )

        # TODO: Check for path in filename%type
        self.work_input_path = os.path.join(self.work_path, 'INPUT')
        self.work_init_path = self.work_input_path
        # TODO: Check for path in filename%restart_out
        self.work_restart_path = os.path.join(self.work_path, 'RESTART')

    def setup(self):
        super(Cable, self).setup()

        if self.prior_restart_path:
            self.cable_nml['cable']['spinup'] = False
        else:
            self.cable_nml['cable']['spinup'] = True

        # Write modified namelist file to work dir
        self.cable_nml.write(
            os.path.join(self.work_path, self.cable_nml_fname),
            force=True
        )

    def archive(self, **kwargs):

        super(Cable, self).archive()

        # Archive the restart files
        mkdir_p(self.restart_path)

        restart_files = [f for f in os.listdir(self.work_restart_path)
                         if f.endswith('restart.nc')]

        for f in restart_files:
            f_src = os.path.join(self.work_restart_path, f)
            shutil.move(f_src, self.restart_path)

        os.rmdir(self.work_restart_path)

        # Move all logs into a logs subdir
        log_path = os.path.join(self.work_path, 'logs')
        mkdir_p(log_path)
        log_files = [f for f in os.listdir(self.work_path)
                     if f.startswith('cable_log')]
        for f in log_files:
            f_src = os.path.join(self.work_path, f)
            shutil.move(f_src, log_path)

    def collate(self):
        pass
