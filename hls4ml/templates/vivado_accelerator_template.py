from hls4ml.templates.vivado_template import VivadoBackend
import os
from shutil import copyfile


class VivadoAcceleratorBackend(VivadoBackend):
    def __init__(self):
        super(VivadoAcceleratorBackend, self).__init__(name='VivadoAccelerator')

    def make_bitfile(model):
        curr_dir = os.getcwd()
        os.chdir(model.config.get_output_dir())
        try:
            os.system('vivado -mode batch -source design.tcl')
        except:
            print("Something went wrong, check the Vivado logs")
        # These should work but Vivado seems to return before the files are written...
        # copyfile('{}_vivado_accelerator/project_1.runs/impl_1/design_1_wrapper.bit'.format(model.config.get_project_name()), './{}.bit'.format(model.config.get_project_name()))
        # copyfile('{}_vivado_accelerator/project_1.srcs/sources_1/bd/design_1/hw_handoff/design_1.hwh'.format(model.config.get_project_name()), './{}.hwh'.format(model.config.get_project_name()))
        os.chdir(curr_dir)

    def make_xclbin(model, platform='xilinx_u50_gen3x16_xdma_201920_3'):
        """

        Parameters
        ----------
        - model : compiled and built hls_model.
        - platform : development Target Platform, must be installed first. On the host machine is required only the
                     deployment target platform, both can be found on the Getting Started section of the Alveo card.
        """
        curr_dir = os.getcwd()
        os.chdir(model.config.get_output_dir())
        os.makedirs('xo_files', exist_ok=True)
        try:
            os.system('vivado -mode batch -source design.tcl')
        except:
            print("Something went wrong, check the Vivado logs")
        # These should work but Vivado seems to return before the files are written...
        # copyfile('{}_vivado_accelerator/project_1.runs/impl_1/design_1_wrapper.bit'.format(model.config.get_project_name()), './{}.bit'.format(model.config.get_project_name()))
        # copyfile('{}_vivado_accelerator/project_1.srcs/sources_1/bd/design_1/hw_handoff/design_1.hwh'.format(model.config.get_project_name()), './{}.hwh'.format(model.config.get_project_name()))
        # TODO improve the line below
        ip_repo_path = model.config.get_output_dir() + '/myproject_prj/solution1/impl/ip'
        os.makedirs('xclbin_files', exist_ok=True)
        os.chdir(model.config.get_output_dir() + '/xclbin_files')
        # TODO Add other platforms
        vitis_cmd = "v++ -t hw --platform " + platform + " --link ../xo_files/myproject_kernel.xo -o'myproject_kernel.xclbin' --user_ip_repo_paths " + ip_repo_path
        try:
            os.system(vitis_cmd)
        except:
            print("Something went wrong, check the Vitis/Vivado logs")
        os.chdir(curr_dir)

    def create_initial_config(self, board='pynq-z2', part=None, clock_period=5, io_type='io_parallel', interface='axi_stream',
                              driver='python', input_type='float', output_type='float'):
        '''
        Create initial accelerator config with default parameters
        Args:
            device: one of the keys defined in supported_boards.json
            clock_period: clock period passed to hls project
            io_type: io_parallel or io_stream
            interface: `axi_stream`: generate hardware designs and drivers which exploit axi stream channels.
                       `axi_master`: generate hardware designs and drivers which exploit axi master channels.
                       `axi_lite` : generate hardware designs and drivers which exploit axi lite channels. (Don't use it
                       to exchange large amount of data)
            driver: `python`: generates the python driver to use the accelerator in the PYNQ stack.
                    `c`: generates the c driver to use the accelerator bare-metal.
            input_type: the wrapper input precision. Can be `float` or an `ap_type`. Note: VivadoAcceleratorBackend
                             will round the number of bits used to the next power-of-2 value.
            output_type: the wrapper output precision. Can be `float` or an `ap_type`. Note:
                              VivadoAcceleratorBackend will round the number of bits used to the next power-of-2 value.

        Returns:
            populated config
        '''
        board = board if board is not None else 'pynq-z2'
        config = super(VivadoAcceleratorBackend, self).create_initial_config(part, board, clock_period, io_type)
        config['AcceleratorConfig'] = {}
        config['AcceleratorConfig']['Interface'] = interface  # axi_stream, axi_master, axi_lite
        config['AcceleratorConfig']['Driver'] = driver
        config['AcceleratorConfig']['Precision'] = {}
        config['AcceleratorConfig']['Precision']['Input'] = {}
        config['AcceleratorConfig']['Precision']['Output'] = {}
        config['AcceleratorConfig']['Precision']['Input'] = input_type  # float, double or ap_fixed<a,b>
        config['AcceleratorConfig']['Precision']['Output'] = output_type  # float, double or ap_fixed<a,b>
        return config
