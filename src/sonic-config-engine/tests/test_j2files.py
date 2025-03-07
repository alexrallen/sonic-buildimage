import json
import os
import shutil
import subprocess

from unittest import TestCase
import tests.common_utils as utils


class TestJ2Files(TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.script_file = utils.PYTHON_INTERPRETTER + ' ' + os.path.join(self.test_dir, '..', 'sonic-cfggen')
        self.simple_minigraph = os.path.join(self.test_dir, 'simple-sample-graph.xml')
        self.t0_minigraph = os.path.join(self.test_dir, 't0-sample-graph.xml')
        self.t0_mvrf_minigraph = os.path.join(self.test_dir, 't0-sample-graph-mvrf.xml')
        self.pc_minigraph = os.path.join(self.test_dir, 'pc-test-graph.xml')
        self.t0_port_config = os.path.join(self.test_dir, 't0-sample-port-config.ini')
        self.l1_l3_port_config = os.path.join(self.test_dir, 'l1-l3-sample-port-config.ini')
        self.t0_7050cx3_port_config = os.path.join(self.test_dir, 't0_7050cx3_d48c8_port_config.ini')
        self.t1_mlnx_minigraph = os.path.join(self.test_dir, 't1-sample-graph-mlnx.xml')
        self.mlnx_port_config = os.path.join(self.test_dir, 'sample-port-config-mlnx.ini')
        self.dell6100_t0_minigraph = os.path.join(self.test_dir, 'sample-dell-6100-t0-minigraph.xml')
        self.arista7050_t0_minigraph = os.path.join(self.test_dir, 'sample-arista-7050-t0-minigraph.xml')
        self.arista7800r3_48cq2_lc_t2_minigraph = os.path.join(self.test_dir, 'sample-arista-7800r3-48cq2-lc-t2-minigraph.xml')
        self.multi_asic_minigraph = os.path.join(self.test_dir, 'multi_npu_data', 'sample-minigraph.xml')
        self.multi_asic_port_config = os.path.join(self.test_dir, 'multi_npu_data', 'sample_port_config-0.ini')
        self.dell9332_t1_minigraph = os.path.join(self.test_dir, 'sample-dell-9332-t1-minigraph.xml')
        self.radv_test_minigraph = os.path.join(self.test_dir, 'radv-test-sample-graph.xml')
        self.no_ip_helper_minigraph = os.path.join(self.test_dir, 't0-sample-no-ip-helper-graph.xml')
        self.output_file = os.path.join(self.test_dir, 'output')
        os.environ["CFGGEN_UNIT_TESTING"] = "2"

    def run_script(self, argument):
        print('CMD: sonic-cfggen ' + argument)
        output = subprocess.check_output(self.script_file + ' ' + argument, shell=True)

        if utils.PY3x:
            output = output.decode()

        return output

    def run_diff(self, file1, file2):
        return subprocess.check_output('diff -u {} {} || true'.format(file1, file2), shell=True)

    def create_machine_conf(self, platform, vendor):
        file_exist = True
        dir_exist = True
        mode = {'arista': 'aboot',
                'dell': 'onie',
                'mellanox': 'onie'
               }
        echo_cmd = "echo '{}_platform={}' | sudo tee -a /host/machine.conf > /dev/null".format(mode[vendor], platform)
        if not os.path.exists('/host/machine.conf'):
            file_exist = False
            if not os.path.isdir('/host'):
                dir_exist = False
                os.system('sudo mkdir /host')
            os.system('sudo touch /host/machine.conf')
            os.system(echo_cmd)

        return file_exist, dir_exist

    def remove_machine_conf(self, file_exist, dir_exist):
        if not file_exist:
            os.system('sudo rm -f /host/machine.conf')

        if not dir_exist:
            os.system('sudo rmdir /host')

    def test_interfaces(self):
        interfaces_template = os.path.join(self.test_dir, '..', '..', '..', 'files', 'image_config', 'interfaces', 'interfaces.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -a \'{\"hwaddr\":\"e4:1d:2d:a5:f3:ad\"}\' -t ' + interfaces_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(utils.cmp(os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'interfaces'), self.output_file))

        argument = '-m ' + self.t0_mvrf_minigraph + ' -p ' + self.t0_port_config + ' -a \'{\"hwaddr\":\"e4:1d:2d:a5:f3:ad\"}\' -t ' + interfaces_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(utils.cmp(os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'mvrf_interfaces'), self.output_file))

    def test_ports_json(self):
        ports_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent', 'ports.json.j2')
        argument = '-m ' + self.simple_minigraph + ' -p ' + self.t0_port_config + ' -t ' + ports_template + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(utils.cmp(os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'ports.json'), self.output_file))

    def test_dhcp_relay(self):
        # Test generation of wait_for_intf.sh
        template_path = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-dhcp-relay', 'wait_for_intf.sh.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + template_path + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(utils.cmp(os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'wait_for_intf.sh'), self.output_file))

        # Test generation of docker-dhcp-relay.supervisord.conf
        template_path = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-dhcp-relay', 'docker-dhcp-relay.supervisord.conf.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + template_path + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(utils.cmp(os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'docker-dhcp-relay.supervisord.conf'), self.output_file))

        # Test generation of docker-dhcp-relay.supervisord.conf when a vlan is missing ip/ipv6 helpers
        template_path = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-dhcp-relay', 'docker-dhcp-relay.supervisord.conf.j2')
        argument = '-m ' + self.no_ip_helper_minigraph + ' -p ' + self.t0_port_config + ' -t ' + template_path + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(utils.cmp(os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'docker-dhcp-relay-no-ip-helper.supervisord.conf'), self.output_file))

    def test_radv(self):
        # Test generation of radvd.conf with multiple ipv6 prefixes
        template_path = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-router-advertiser', 'radvd.conf.j2')
        argument = '-m ' + self.radv_test_minigraph + ' -p ' + self.t0_port_config + ' -t ' + template_path + ' > ' + self.output_file
        self.run_script(argument)
        self.assertTrue(utils.cmp(os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'radvd.conf'), self.output_file))

    def test_lldp(self):
        lldpd_conf_template = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-lldp', 'lldpd.conf.j2')

        expected_mgmt_ipv4 = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'lldp_conf', 'lldpd-ipv4-iface.conf')
        expected_mgmt_ipv6 = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'lldp_conf', 'lldpd-ipv6-iface.conf')
        expected_mgmt_ipv4_and_ipv6 = expected_mgmt_ipv4

        # Test generation of lldpd.conf if IPv4 and IPv6 management interfaces exist
        mgmt_iface_ipv4_and_ipv6_json = os.path.join(self.test_dir, "data", "lldp", "mgmt_iface_ipv4_and_ipv6.json")
        argument = '-j {} -t {} > {}'.format(mgmt_iface_ipv4_and_ipv6_json, lldpd_conf_template, self.output_file)
        self.run_script(argument)
        self.assertTrue(utils.cmp(expected_mgmt_ipv4_and_ipv6, self.output_file))

        # Test generation of lldpd.conf if management interface IPv4 only exist
        mgmt_iface_ipv4_json = os.path.join(self.test_dir, "data", "lldp", "mgmt_iface_ipv4.json")
        argument = '-j {} -t {} > {}'.format(mgmt_iface_ipv4_json, lldpd_conf_template, self.output_file)
        self.run_script(argument)
        self.assertTrue(utils.cmp(expected_mgmt_ipv4, self.output_file))

        # Test generation of lldpd.conf if Management interface IPv6 only exist
        mgmt_iface_ipv6_json = os.path.join(self.test_dir, "data", "lldp", "mgmt_iface_ipv6.json")
        argument = '-j {} -t {} > {}'.format(mgmt_iface_ipv6_json, lldpd_conf_template, self.output_file)
        self.run_script(argument)
        self.assertTrue(utils.cmp(expected_mgmt_ipv6, self.output_file))

    def test_ipinip(self):
        ipinip_file = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent', 'ipinip.json.j2')
        argument = '-m ' + self.t0_minigraph + ' -p ' + self.t0_port_config + ' -t ' + ipinip_file + ' > ' + self.output_file
        self.run_script(argument)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'ipinip.json')
        assert utils.cmp(sample_output_file, self.output_file), self.run_diff(sample_output_file, self.output_file)

    def test_l2switch_template(self):
        argument = '-k Mellanox-SN2700 --preset l2 -p ' + self.t0_port_config
        output = self.run_script(argument)
        output_json = json.loads(output)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'l2switch.json')
        with open(sample_output_file) as sample_output_fd:
            sample_output_json = json.load(sample_output_fd)

        self.assertTrue(json.dumps(sample_output_json, sort_keys=True) == json.dumps(output_json, sort_keys=True))

        template_dir = os.path.join(self.test_dir, '..', 'data', 'l2switch.j2')
        argument = '-t ' + template_dir + ' -k Mellanox-SN2700 -p ' + self.t0_port_config
        output = self.run_script(argument)
        output_json = json.loads(output)

        self.assertTrue(json.dumps(sample_output_json, sort_keys=True) == json.dumps(output_json, sort_keys=True))
    
    def test_l1_ports_template(self):
        argument = '-k 32x1000Gb --preset l1 -p ' + self.l1_l3_port_config
        output = self.run_script(argument)
        output_json = json.loads(output)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'l1_intfs.json')
        with open(sample_output_file) as sample_output_fd:
            sample_output_json = json.load(sample_output_fd)

        self.assertTrue(json.dumps(sample_output_json, sort_keys=True) == json.dumps(output_json, sort_keys=True))

        template_dir = os.path.join(self.test_dir, '..', 'data', 'l1intf.j2')
        argument = '-t ' + template_dir + ' -k 32x1000Gb -p ' + self.l1_l3_port_config
        output = self.run_script(argument)
        output_json = json.loads(output)

        self.assertTrue(json.dumps(sample_output_json, sort_keys=True) == json.dumps(output_json, sort_keys=True))

    def test_l3_ports_template(self):
        argument = '-k 32x1000Gb --preset l3 -p ' + self.l1_l3_port_config
        output = self.run_script(argument)
        output_json = json.loads(output)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'l3_intfs.json')
        with open(sample_output_file) as sample_output_fd:
            sample_output_json = json.load(sample_output_fd)

        self.assertTrue(json.dumps(sample_output_json, sort_keys=True) == json.dumps(output_json, sort_keys=True))

        template_dir = os.path.join(self.test_dir, '..', 'data', 'l3intf.j2')
        argument = '-t ' + template_dir + ' -k 32x1000Gb -p ' + self.l1_l3_port_config
        output = self.run_script(argument)
        output_json = json.loads(output)

        self.assertTrue(json.dumps(sample_output_json, sort_keys=True) == json.dumps(output_json, sort_keys=True))

    def test_l2switch_template_dualtor(self):
        extra_args = {
            "is_dualtor": True,
            "uplinks": [
                "Ethernet24", "Ethernet28", "Ethernet32", "Ethernet36",
                "Ethernet88", "Ethernet92", "Ethernet96", "Ethernet100"
            ],
            "downlinks": [
                "Ethernet0", "Ethernet4", "Ethernet8", "Ethernet12",
                "Ethernet16", "Ethernet20", "Ethernet40", "Ethernet44",
                "Ethernet48", "Ethernet52", "Ethernet56", "Ethernet60",
                "Ethernet64", "Ethernet68", "Ethernet72", "Ethernet76",
                "Ethernet80", "Ethernet84", "Ethernet104", "Ethernet108",
                "Ethernet112", "Ethernet116", "Ethernet120", "Ethernet124"
            ]
        }
        argument = '-a \'{}\' -k Arista-7050CX3-32S-D48C8 --preset l2 -p {}'.format(
            json.dumps(extra_args), self.t0_7050cx3_port_config
        )
        output = self.run_script(argument)
        output_json = json.loads(output)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'l2switch_dualtor.json')
        with open(sample_output_file) as sample_output_fd:
            sample_output_json = json.load(sample_output_fd)
        self.maxDiff = None
        self.assertEqual(sample_output_json, output_json)

    def test_qos_arista7050_render_template(self):
        arista_dir_path = os.path.join(self.test_dir, '..', '..', '..', 'device', 'arista', 'x86_64-arista_7050_qx32s', 'Arista-7050-QX-32S')
        qos_file = os.path.join(arista_dir_path, 'qos.json.j2')
        port_config_ini_file = os.path.join(arista_dir_path, 'port_config.ini')

        # copy qos_config.j2 to the Arista 7050 directory to have all templates in one directory
        qos_config_file = os.path.join(self.test_dir, '..', '..', '..', 'files', 'build_templates', 'qos_config.j2')
        shutil.copy2(qos_config_file, arista_dir_path)

        argument = '-m ' + self.arista7050_t0_minigraph + ' -p ' + port_config_ini_file + ' -t ' + qos_file + ' > ' + self.output_file
        self.run_script(argument)

        # cleanup
        qos_config_file_new = os.path.join(arista_dir_path, 'qos_config.j2')
        os.remove(qos_config_file_new)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'qos-arista7050.json')
        assert utils.cmp(sample_output_file, self.output_file), self.run_diff(sample_output_file, self.output_file)

    def do_test_qos_and_buffer_arista7800r3_48cq2_lc_render_template(self, platform, hwsku):
        arista_dir_path = os.path.join(self.test_dir, '..', '..', '..', 'device', 'arista', platform, hwsku)
        qos_file = os.path.join(arista_dir_path, 'qos.json.j2')
        buffer_file = os.path.join(arista_dir_path, 'buffers.json.j2')
        port_config_ini_file = os.path.join(arista_dir_path, 'port_config.ini')

        # copy qos_config.j2 and buffer_config.j2 to the Arista 7800r3_48cq2_lc directory to have all templates in one directory
        qos_config_file = os.path.join(self.test_dir, '..', '..', '..', 'files', 'build_templates', 'qos_config.j2')
        shutil.copy2(qos_config_file, arista_dir_path)
        buffer_config_file = os.path.join(self.test_dir, '..', '..', '..', 'files', 'build_templates', 'buffers_config.j2')
        shutil.copy2(buffer_config_file, arista_dir_path)

        for template_file, cfg_file, sample_output_file in [(qos_file, 'qos_config.j2', 'qos-arista7800r3-48cq2-lc.json'),
                                                            (buffer_file, 'buffers_config.j2', 'buffer-arista7800r3-48cq2-lc.json') ]:
            argument = '-m ' + self.arista7800r3_48cq2_lc_t2_minigraph + ' -p ' + port_config_ini_file + ' -t ' + template_file + ' > ' + self.output_file
            self.run_script(argument)

            # cleanup
            cfg_file_new = os.path.join(arista_dir_path, cfg_file)
            os.remove(cfg_file_new)

            sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, sample_output_file)
            assert utils.cmp(sample_output_file, self.output_file), self.run_diff(sample_output_file, self.output_file)

    def test_qos_and_buffer_arista7800r3_48cq2_lc_render_template(self):
        self.do_test_qos_and_buffer_arista7800r3_48cq2_lc_render_template('x86_64-arista_7800r3_48cq2_lc', 'Arista-7800R3-48CQ2-C48')

    def test_qos_and_buffer_arista7800r3_48cqm2_lc_render_template(self):
        self.do_test_qos_and_buffer_arista7800r3_48cq2_lc_render_template('x86_64-arista_7800r3_48cqm2_lc', 'Arista-7800R3-48CQM2-C48')

    def test_qos_dell9332_render_template(self):
        dell_dir_path = os.path.join(self.test_dir, '..', '..', '..', 'device', 'dell', 'x86_64-dellemc_z9332f_d1508-r0', 'DellEMC-Z9332f-O32')
        qos_file = os.path.join(dell_dir_path, 'qos.json.j2')
        port_config_ini_file = os.path.join(dell_dir_path, 'port_config.ini')

        # copy qos_config.j2 to the Dell Z9332 directory to have all templates in one directory
        qos_config_file = os.path.join(self.test_dir, '..', '..', '..', 'files', 'build_templates', 'qos_config.j2')
        shutil.copy2(qos_config_file, dell_dir_path)

        argument = '-m ' + self.dell9332_t1_minigraph + ' -p ' + port_config_ini_file + ' -t ' + qos_file + ' > ' + self.output_file
        self.run_script(argument)

        # cleanup
        qos_config_file_new = os.path.join(dell_dir_path, 'qos_config.j2')
        os.remove(qos_config_file_new)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'qos-dell9332.json')
        assert utils.cmp(sample_output_file, self.output_file), self.run_diff(sample_output_file, self.output_file)
   
    def test_qos_dell6100_render_template(self):
        dell_dir_path = os.path.join(self.test_dir, '..', '..', '..', 'device', 'dell', 'x86_64-dell_s6100_c2538-r0', 'Force10-S6100')
        qos_file = os.path.join(dell_dir_path, 'qos.json.j2')
        port_config_ini_file = os.path.join(dell_dir_path, 'port_config.ini')

        # copy qos_config.j2 to the Dell S6100 directory to have all templates in one directory
        qos_config_file = os.path.join(self.test_dir, '..', '..', '..', 'files', 'build_templates', 'qos_config.j2')
        shutil.copy2(qos_config_file, dell_dir_path)

        argument = '-m ' + self.dell6100_t0_minigraph + ' -p ' + port_config_ini_file + ' -t ' + qos_file + ' > ' + self.output_file
        self.run_script(argument)

        # cleanup
        qos_config_file_new = os.path.join(dell_dir_path, 'qos_config.j2')
        os.remove(qos_config_file_new)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, 'qos-dell6100.json')
        assert utils.cmp(sample_output_file, self.output_file), self.run_diff(sample_output_file, self.output_file)

    def test_qos_dscp_remapping_render_template(self):
        if utils.PYvX_DIR != 'py3':
            # Skip on python2 as the change will not be backported to previous version
            return

        dir_paths = [
            '../../../device/arista/x86_64-arista_7050cx3_32s/Arista-7050CX3-32S-D48C8',
            '../../../device/arista/x86_64-arista_7260cx3_64/Arista-7260CX3-D108C8',
            '../../../device/arista/x86_64-arista_7260cx3_64/Arista-7260CX3-C64',
            '../../../device/arista/x86_64-arista_7050cx3_32s/Arista-7050CX3-32S-D48C8',
            '../../../device/arista/x86_64-arista_7260cx3_64/Arista-7260CX3-D108C8',
            '../../../device/arista/x86_64-arista_7260cx3_64/Arista-7260CX3-C64'
            ]
        sample_outputs = [
            'qos-arista7050cx3-dualtor.json',
            'qos-arista7260-dualtor.json',
            'qos-arista7260-t1.json',
            'qos-arista7050cx3-dualtor-remap-disabled.json',
            'qos-arista7260-dualtor-remap-disabled.json',
            'qos-arista7260-t1-remap-disabled.json'
        ]
        sample_minigraph_files = [
            'sample-arista-7050cx3-dualtor-minigraph.xml',
            'sample-arista-7260-dualtor-minigraph.xml',
            'sample-arista-7260-t1-minigraph.xml',
            'sample-arista-7050cx3-dualtor-minigraph-remap-disabled.xml',
            'sample-arista-7260-dualtor-minigraph-remap-disabled.xml',
            'sample-arista-7260-t1-minigraph-remap-disabled.xml'
        ]
        for i, path in enumerate(dir_paths):
            device_template_path = os.path.join(self.test_dir, path)
            sample_output = sample_outputs[i]
            sample_minigraph_file = os.path.join(self.test_dir,sample_minigraph_files[i])
            qos_file = os.path.join(device_template_path, 'qos.json.j2')
            port_config_ini_file = os.path.join(device_template_path, 'port_config.ini')
            test_output = os.path.join(self.test_dir, 'output.json')

            # copy qos_config.j2 to the target directory to have all templates in one directory
            qos_config_file = os.path.join(self.test_dir, '..', '..', '..', 'files', 'build_templates', 'qos_config.j2')
            shutil.copy2(qos_config_file, device_template_path)

            argument = '-m ' + sample_minigraph_file + ' -p ' + port_config_ini_file + ' -t ' + qos_file + ' > ' + test_output
            self.run_script(argument)

            # cleanup
            qos_config_file_new = os.path.join(device_template_path, 'qos_config.j2')
            os.remove(qos_config_file_new)

            sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, sample_output)
            assert utils.cmp(sample_output_file, test_output)
            os.remove(test_output)

    def test_config_brcm_render_template(self):
        if utils.PYvX_DIR != 'py3':
            #Skip on python2 as the change will not be backported to previous version
            return

        config_bcm_sample_outputs = [
            'arista7050cx3-dualtor.config.bcm',
            'arista7260-dualtor.config.bcm',
            'arista7260-t1.config.bcm'
        ]
        sample_minigraph_files = [
            'sample-arista-7050cx3-dualtor-minigraph.xml',
            'sample-arista-7260-dualtor-minigraph.xml',
            'sample-arista-7260-t1-minigraph.xml'
        ]
        for i, config in enumerate(config_bcm_sample_outputs):
            device_template_path = os.path.join(self.test_dir, './data/j2_template')
            config_sample_output = config_bcm_sample_outputs[i]
            sample_minigraph_file = os.path.join(self.test_dir,sample_minigraph_files[i])
            port_config_ini_file = os.path.join(device_template_path, 'port_config.ini')
            config_bcm_file = os.path.join(device_template_path, 'config.bcm.j2')
            config_test_output = os.path.join(self.test_dir, 'config_output.bcm')

            argument = '-m ' + sample_minigraph_file + ' -p ' + port_config_ini_file + ' -t ' + config_bcm_file + ' > ' + config_test_output
            self.run_script(argument)

            #check output config.bcm
            config_sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, config_sample_output)
            assert utils.cmp(config_sample_output_file, config_test_output)
            os.remove(config_test_output)

    def _test_buffers_render_template(self, vendor, platform, sku, minigraph, buffer_template, expected):
        file_exist, dir_exist = self.create_machine_conf(platform, vendor)
        dir_path = os.path.join(self.test_dir, '..', '..', '..', 'device', vendor, platform, sku)
        buffers_file = os.path.join(dir_path, buffer_template)
        port_config_ini_file = os.path.join(dir_path, 'port_config.ini')

        # copy buffers_config.j2 to the SKU directory to have all templates in one directory
        buffers_config_file = os.path.join(self.test_dir, '..', '..', '..', 'files', 'build_templates', 'buffers_config.j2')
        shutil.copy2(buffers_config_file, dir_path)

        minigraph = os.path.join(self.test_dir, minigraph)                              
        argument = '-m ' + minigraph + ' -p ' + port_config_ini_file + ' -t ' + buffers_file + ' > ' + self.output_file
        self.run_script(argument)

        # cleanup
        buffers_config_file_new = os.path.join(dir_path, 'buffers_config.j2')
        os.remove(buffers_config_file_new)
        self.remove_machine_conf(file_exist, dir_exist)

        sample_output_file = os.path.join(self.test_dir, 'sample_output', utils.PYvX_DIR, expected)
        assert utils.cmp(sample_output_file, self.output_file), self.run_diff(sample_output_file, self.output_file)

    def test_buffers_dell6100_render_template(self):
        self._test_buffers_render_template('dell', 'x86_64-dell_s6100_c2538-r0', 'Force10-S6100', 'sample-dell-6100-t0-minigraph.xml', 'buffers.json.j2', 'buffers-dell6100.json')

    def test_buffers_mellanox2700_render_template(self):
        self._test_buffers_render_template('mellanox', 'x86_64-mlnx_msn2700-r0', 'Mellanox-SN2700-D48C8', 'sample-mellanox-2700-t0-minigraph.xml', 'buffers.json.j2', 'buffers-mellanox2700.json')

    def test_buffers_mellanox2410_render_template(self):
        self._test_buffers_render_template('mellanox', 'x86_64-mlnx_msn2410-r0', 'ACS-MSN2410', 'sample-mellanox-2410-t1-minigraph.xml', 'buffers.json.j2', 'buffers-mellanox2410.json')

    def test_buffers_mellanox2410_dynamic_render_template(self):
        self._test_buffers_render_template('mellanox', 'x86_64-mlnx_msn2410-r0', 'ACS-MSN2410', 'sample-mellanox-2410-t1-minigraph.xml', 'buffers_dynamic.json.j2', 'buffers-mellanox2410-dynamic.json')

    def test_extra_lossless_buffer_for_tunnel_remapping(self):
        if utils.PYvX_DIR != 'py3':
            # Skip on python2 as the change will not be backported to previous version
            return
        
        TEST_DATA = [
            # (vendor, platform, sku, minigraph, buffer_template, sample_output )
            ('arista', 'x86_64-arista_7050cx3_32s', 'Arista-7050CX3-32S-D48C8', 'sample-arista-7050cx3-dualtor-minigraph.xml', 'buffers.json.j2', 'buffer-arista7050cx3-dualtor.json'),
            ('arista', 'x86_64-arista_7050cx3_32s', 'Arista-7050CX3-32S-D48C8', 'sample-arista-7050cx3-dualtor-minigraph-remap-disabled.xml', 'buffers.json.j2', 'buffer-arista7050cx3-dualtor-remap-disabled.json'),
            ('arista', 'x86_64-arista_7260cx3_64', 'Arista-7260CX3-D108C8', 'sample-arista-7260-dualtor-minigraph.xml', 'buffers.json.j2', 'buffer-arista7260-dualtor.json'),
            ('arista', 'x86_64-arista_7260cx3_64', 'Arista-7260CX3-D108C8', 'sample-arista-7260-dualtor-minigraph-remap-disabled.xml', 'buffers.json.j2', 'buffer-arista7260-dualtor-remap-disabled.json'),
            ('arista', 'x86_64-arista_7260cx3_64', 'Arista-7260CX3-C64', 'sample-arista-7260-t1-minigraph.xml', 'buffers.json.j2', 'buffer-arista7260-t1.json'),
            ('arista', 'x86_64-arista_7260cx3_64', 'Arista-7260CX3-C64', 'sample-arista-7260-t1-minigraph-remap-disabled.xml', 'buffers.json.j2', 'buffer-arista7260-t1-remap-disabled.json')
        ]

        for test_data in TEST_DATA:
            self._test_buffers_render_template(vendor=test_data[0],
                                                platform=test_data[1],
                                                sku=test_data[2],
                                                minigraph=test_data[3],
                                                buffer_template=test_data[4],
                                                expected=test_data[5])

    def test_ipinip_multi_asic(self):
        ipinip_file = os.path.join(self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent', 'ipinip.json.j2')
        argument = '-m ' + self.multi_asic_minigraph + ' -p ' + self.multi_asic_port_config + ' -t ' + ipinip_file  +  ' -n asic0 '  + ' > ' + self.output_file
        print(argument)
        self.run_script(argument) 
        sample_output_file = os.path.join(self.test_dir, 'multi_npu_data', utils.PYvX_DIR, 'ipinip.json')
        assert utils.cmp(sample_output_file, self.output_file), self.run_diff(sample_output_file, self.output_file)

    def test_swss_switch_render_template(self):
        switch_template = os.path.join(
            self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent',
            'switch.json.j2'
        )
        constants_yml = os.path.join(
            self.test_dir, '..', '..', '..', 'files', 'image_config',
            'constants', 'constants.yml'
        )
        test_list = {
            "t1": {
                "graph": self.t1_mlnx_minigraph,
                "port_config": self.mlnx_port_config,
                "output": "t1-switch.json"
            },
            "t0": {
                "graph": self.t0_minigraph,
                "port_config": self.t0_port_config,
                "output": "t0-switch.json"
            },
        }
        for _, v in test_list.items():
            argument = " -m {} -p {} -y {} -t {} > {}".format(
                v["graph"], v["port_config"], constants_yml, switch_template, self.output_file
            )
            sample_output_file = os.path.join(
                self.test_dir, 'sample_output', v["output"]
            )
            self.run_script(argument)
            assert utils.cmp(sample_output_file, self.output_file), self.run_diff(sample_output_file, self.output_file)

    def test_swss_switch_render_template_multi_asic(self):
        # verify the ECMP hash seed changes per namespace
        switch_template = os.path.join(
            self.test_dir, '..', '..', '..', 'dockers', 'docker-orchagent',
            'switch.json.j2'
        )
        constants_yml = os.path.join(
            self.test_dir, '..', '..', '..', 'files', 'image_config',
            'constants', 'constants.yml'
        )
        test_list = {
            "0": {
                "namespace_id": "1",
                "output": "t0-switch-masic1.json"
            },
            "1": {
                "namespace_id": "3",
                "output": "t0-switch-masic3.json"
            },
        }
        for _, v in test_list.items():
            os.environ["NAMESPACE_ID"] = v["namespace_id"]
            argument = " -m {} -y {} -t {} > {}".format(
                self.t1_mlnx_minigraph, constants_yml, switch_template,
                self.output_file
            )
            sample_output_file = os.path.join(
                self.test_dir, 'sample_output', v["output"]
            )
            self.run_script(argument)
            assert utils.cmp(sample_output_file, self.output_file), self.run_diff(sample_output_file, self.output_file)
        os.environ["NAMESPACE_ID"] = ""

    def test_ndppd_conf(self):
        conf_template = os.path.join(self.test_dir, "ndppd.conf.j2")
        vlan_interfaces_json = os.path.join(self.test_dir, "data", "ndppd", "vlan_interfaces.json")
        expected = os.path.join(self.test_dir, "sample_output", utils.PYvX_DIR, "ndppd.conf")

        argument = '-j {} -t {} > {}'.format(vlan_interfaces_json, conf_template, self.output_file)
        self.run_script(argument)
        assert utils.cmp(expected, self.output_file), self.run_diff(expected, self.output_file)

    def test_ntp_conf(self):
        conf_template = os.path.join(self.test_dir, "ntp.conf.j2")
        ntp_interfaces_json = os.path.join(self.test_dir, "data", "ntp", "ntp_interfaces.json")
        expected = os.path.join(self.test_dir, "sample_output", utils.PYvX_DIR, "ntp.conf")

        argument = '-j {} -t {} > {}'.format(ntp_interfaces_json, conf_template, self.output_file)
        self.run_script(argument)
        assert utils.cmp(expected, self.output_file), self.run_diff(expected, self.output_file)

    def tearDown(self):
        os.environ["CFGGEN_UNIT_TESTING"] = ""
        try:
            os.remove(self.output_file)
        except OSError:
            pass
