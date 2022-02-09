import ml_collections

NUM_RES = 'num residues placeholder'
NUM_MSA_SEQ = 'msa placeholder'
NUM_EXTRA_SEQ = 'extra msa placeholder'
NUM_TEMPLATES = 'num templates placeholder'

tiny_config = ml_collections.ConfigDict({
	'data': {
		'common': {
			'masked_msa': {
				'profile_prob': 0.1,
				'same_prob': 0.1,
				'uniform_prob': 0.1
			},
			'max_extra_msa': 256,
			'msa_cluster_features': True,
			'num_recycle': 0,
			'reduce_msa_clusters_by_max_templates': False,
			'resample_msa_in_recycling': False,
			'use_templates': False,
		},
		'eval': {
			'feat': {
				'aatype': [NUM_RES],
				'all_atom_mask': [NUM_RES, None],
				'all_atom_positions': [NUM_RES, None, None],
				'alt_chi_angles': [NUM_RES, None],
				'atom14_alt_gt_exists': [NUM_RES, None],
				'atom14_alt_gt_positions': [NUM_RES, None, None],
				'atom14_atom_exists': [NUM_RES, None],
				'atom14_atom_is_ambiguous': [NUM_RES, None],
				'atom14_gt_exists': [NUM_RES, None],
				'atom14_gt_positions': [NUM_RES, None, None],
				'atom37_atom_exists': [NUM_RES, None],
				'backbone_affine_mask': [NUM_RES],
				'backbone_affine_tensor': [NUM_RES, None],
				'bert_mask': [NUM_MSA_SEQ, NUM_RES],
				'chi_angles_sin_cos': [NUM_RES, None, None],
				'chi_mask': [NUM_RES, None],
				'extra_deletion_value': [NUM_EXTRA_SEQ, NUM_RES],
				'extra_has_deletion': [NUM_EXTRA_SEQ, NUM_RES],
				'extra_msa': [NUM_EXTRA_SEQ, NUM_RES],
				'extra_msa_mask': [NUM_EXTRA_SEQ, NUM_RES],
				'extra_msa_row_mask': [NUM_EXTRA_SEQ],
				'is_distillation': [],
				'msa_feat': [NUM_MSA_SEQ, NUM_RES, None],
				'msa_mask': [NUM_MSA_SEQ, NUM_RES],
				'msa_row_mask': [NUM_MSA_SEQ],
				'pseudo_beta': [NUM_RES, None],
				'pseudo_beta_mask': [NUM_RES],
				'random_crop_to_size_seed': [None],
				'residue_index': [NUM_RES],
				'residx_atom14_to_atom37': [NUM_RES, None],
				'residx_atom37_to_atom14': [NUM_RES, None],
				'resolution': [],
				'rigidgroups_alt_gt_frames': [NUM_RES, None, None],
				'rigidgroups_group_exists': [NUM_RES, None],
				'rigidgroups_group_is_ambiguous': [NUM_RES, None],
				'rigidgroups_gt_exists': [NUM_RES, None],
				'rigidgroups_gt_frames': [NUM_RES, None, None],
				'seq_length': [],
				'seq_mask': [NUM_RES],
				'target_feat': [NUM_RES, None],
				'template_aatype': [NUM_TEMPLATES, NUM_RES],
				'template_all_atom_masks': [NUM_TEMPLATES, NUM_RES, None],
				'template_all_atom_positions': [
					NUM_TEMPLATES, NUM_RES, None, None],
				'template_backbone_affine_mask': [NUM_TEMPLATES, NUM_RES],
				'template_backbone_affine_tensor': [
					NUM_TEMPLATES, NUM_RES, None],
				'template_mask': [NUM_TEMPLATES],
				'template_pseudo_beta': [NUM_TEMPLATES, NUM_RES, None],
				'template_pseudo_beta_mask': [NUM_TEMPLATES, NUM_RES],
				'template_sum_probs': [NUM_TEMPLATES, None],
				'true_msa': [NUM_MSA_SEQ, NUM_RES]
			},
			'fixed_size': True,
			'crop_size': 256,
			'subsample_templates': False,  # We want top templates.
			'masked_msa_replace_fraction': 0.15,
			'max_msa_clusters': 512,
			'max_templates': 4,
			'num_ensemble': 1,
		},
	},
	'model': {
		'embeddings_and_evoformer': {
			'evoformer_num_block': 4,
			'evoformer': {
				'msa_row_attention_with_pair_bias': {
					'dropout_rate': 0.15,
					'gating': True,
					'num_head': 4,
					'orientation': 'per_row',
					'shared_dropout': True
				},
				'msa_column_attention': {
					'dropout_rate': 0.0,
					'gating': True,
					'num_head': 4,
					'orientation': 'per_column',
					'shared_dropout': True
				},
				'msa_transition': {
					'dropout_rate': 0.0,
					'num_intermediate_factor': 4,
					'orientation': 'per_row',
					'shared_dropout': True
				},
				'outer_product_mean': {
					'chunk_size': 128,
					'dropout_rate': 0.0,
					'num_outer_channel': 16,
					'orientation': 'per_row',
					'shared_dropout': True
				},
				'triangle_attention_starting_node': {
					'dropout_rate': 0.25,
					'gating': True,
					'num_head': 2,
					'orientation': 'per_row',
					'shared_dropout': True
				},
				'triangle_attention_ending_node': {
					'dropout_rate': 0.25,
					'gating': True,
					'num_head': 2,
					'orientation': 'per_column',
					'shared_dropout': True
				},
				'triangle_multiplication_outgoing': {
					'dropout_rate': 0.25,
					'equation': 'ikc,jkc->ijc',
					'num_intermediate_channel': 32,
					'orientation': 'per_row',
					'shared_dropout': True
				},
				'triangle_multiplication_incoming': {
					'dropout_rate': 0.25,
					'equation': 'kjc,kic->ijc',
					'num_intermediate_channel': 32,
					'orientation': 'per_row',
					'shared_dropout': True
				},
				'pair_transition': {
					'dropout_rate': 0.0,
					'num_intermediate_factor': 4,
					'orientation': 'per_row',
					'shared_dropout': True
				}
			},
			'extra_msa_channel': 32,
			'extra_msa_stack_num_block': 2,
			'max_relative_feature': 32,
			'msa_channel': 64,
			'pair_channel': 64,
			'prev_pos': {
				'min_bin': 3.25,
				'max_bin': 20.75,
				'num_bins': 15
			},
			'recycle_features': False,
			'recycle_pos': False,
			'seq_channel': 384,
			'template': {
				'attention': {
					'gating': False,
					'key_dim': 64,
					'num_head': 4,
					'value_dim': 64
				},
				'dgram_features': {
					'min_bin': 3.25,
					'max_bin': 50.75,
					'num_bins': 39
				},
				'embed_torsion_angles': False,
				'enabled': False,
				'template_pair_stack': {
					'num_block': 2,
					'triangle_attention_starting_node': {
						'dropout_rate': 0.25,
						'gating': True,
						'key_dim': 64,
						'num_head': 4,
						'orientation': 'per_row',
						'shared_dropout': True,
						'value_dim': 64
					},
					'triangle_attention_ending_node': {
						'dropout_rate': 0.25,
						'gating': True,
						'key_dim': 64,
						'num_head': 4,
						'orientation': 'per_column',
						'shared_dropout': True,
						'value_dim': 64
					},
					'triangle_multiplication_outgoing': {
						'dropout_rate': 0.25,
						'equation': 'ikc,jkc->ijc',
						'num_intermediate_channel': 64,
						'orientation': 'per_row',
						'shared_dropout': True
					},
					'triangle_multiplication_incoming': {
						'dropout_rate': 0.25,
						'equation': 'kjc,kic->ijc',
						'num_intermediate_channel': 64,
						'orientation': 'per_row',
						'shared_dropout': True
					},
					'pair_transition': {
						'dropout_rate': 0.0,
						'num_intermediate_factor': 2,
						'orientation': 'per_row',
						'shared_dropout': True
					}
				},
				'max_templates': 4,
				'subbatch_size': 128,
				'use_template_unit_vector': False,
			}
		},
		'global_config': {
			'deterministic': False,
			'subbatch_size': 4,
			'use_remat': False,
			'zero_init': True
		},
		'heads': {
			'distogram': {
				'first_break': 2.3125,
				'last_break': 21.6875,
				'num_bins': 64,
				'weight': 0.3
			},
			'predicted_aligned_error': {
				'max_error_bin': 31.,
				'num_bins': 64,
				'num_channels': 128,
				'filter_by_resolution': False,
				'min_resolution': 0.1,
				'max_resolution': 3.0,
				'weight': 0.0,
			},
			'experimentally_resolved': {
				'filter_by_resolution': False,
				'max_resolution': 3.0,
				'min_resolution': 0.1,
				'weight': 0.01
			},
			'structure_module': {
				'num_layer': 8,
				'fape': {
					'clamp_distance': 10.0,
					'clamp_type': 'relu',
					'loss_unit_distance': 10.0
				},
				'angle_norm_weight': 0.01,
				'chi_weight': 0.5,
				'clash_overlap_tolerance': 1.5,
				'compute_in_graph_metrics': True,
				'dropout': 0.1,
				'num_channel': 384,
				'num_head': 12,
				'num_layer_in_transition': 3,
				'num_point_qk': 4,
				'num_point_v': 8,
				'num_scalar_qk': 16,
				'num_scalar_v': 16,
				'position_scale': 10.0,
				'sidechain': {
					'atom_clamp_distance': 10.0,
					'num_channel': 128,
					'num_residual_block': 2,
					'weight_frac': 0.5,
					'length_scale': 10.,
				},
				'structural_violation_loss_weight': 0.0,
				'violation_tolerance_factor': 12.0,
				'weight': 1.0
			},
			'predicted_lddt': {
				'filter_by_resolution': False,
				'max_resolution': 3.0,
				'min_resolution': 0.1,
				'num_bins': 50,
				'num_channels': 128,
				'weight': 0.01
			},
			'masked_msa': {
				'num_output': 23,
				'weight': 2.0
			},
		},
		'num_recycle': 0,
		'recycle_tol': 0.0,
		'resample_msa_in_recycling': False
	},
})