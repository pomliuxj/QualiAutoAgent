<template>
		<div id="app">
			<transition name="fade"
			            mode="out-in">
				<router-view></router-view>
			</transition>
		</div>
	</template>

	<script>
	export default {
		name: 'app',
		components: {
		}
	}

	</script>

	<style lang="scss">
		$accent: #4F6EF7;
		$accent-soft: rgba(79, 110, 247, 0.07);
		$page-bg: #F3F4F6;
		$text-primary: #111827;
		$text-secondary: #4B5563;
		$text-muted: #9CA3AF;

		body {
			margin: 0px;
			padding: 0px;
			font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
			font-size: 14px;
			-webkit-font-smoothing: antialiased;
			-moz-osx-font-smoothing: grayscale;
			background: $page-bg;
			color: $text-primary;
		}

		#app {
			position: absolute;
			top: 0px;
			bottom: 0px;
			width: 100%;
		}

		.el-submenu [class^=fa] {
			vertical-align: baseline;
			margin-right: 10px;
		}

		.el-menu-item [class^=fa] {
			vertical-align: baseline;
			margin-right: 10px;
		}

		.el-menu--collapse .el-menu .el-submenu, .el-menu--popup {
			min-width: 120px !important;
		}

		.toolbar {
			background: #fff;
			padding: 16px 20px;
			border-radius: 10px;
			margin: 0px 0px 16px 0px;
			border: 1px solid #E5E7EB;
			box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
			.el-form-item {
				margin-bottom: 10px;
			}
		}

		.fade-enter-active,
		.fade-leave-active {
			transition: all .2s ease;
		}

		.fade-enter,
		.fade-leave-active {
			opacity: 0;
		}

		/* ─── Global dropdown menu polish ─────────────── */
		.el-dropdown-menu {
			background: #ffffff;
		border-radius: 12px;
			padding: 6px;
			border: 1px solid #E5E7EB;
			box-shadow:
				0 4px 6px -1px rgba(0, 0, 0, 0.09),
				0 10px 15px -3px rgba(0, 0, 0, 0.09),
				0 20px 40px -8px rgba(0, 0, 0, 0.12);
		}

		.el-dropdown-menu__item {
			border-radius: 8px;
			margin: 2px;
			padding: 9px 14px;
			font-size: 13.5px;
			font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
			font-weight: 450;
			letter-spacing: 0.005em;
			line-height: 1.5;
			transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
			color: #374151;

			i, [class^="fa"] {
				margin-right: 10px;
				font-size: 15px;
				color: $text-muted;
				transition: color 0.18s;
			}

			&:hover {
				background: $accent-soft;
				color: $accent;

				i, [class^="fa"] {
					color: $accent;
				}
			}

			&.is-disabled {
				opacity: 1;
				cursor: default;
				color: inherit;

				&:hover {
					background: transparent;
				}
			}
		}

		.el-dropdown-menu__item--divided {
			&::before {
				background: #F3F4F6;
				margin: 4px 0;
			}
		}

		/* ─── Global button polish ────────────────────── */
		.el-button--primary {
			background: $accent;
			border-color: $accent;

			&:hover, &:focus {
				background: #3D5CE5;
				border-color: #3D5CE5;
			}

			&:active {
				background: #2E4BD4;
				border-color: #2E4BD4;
			}
		}

		/* ─── Global link color ───────────────────────── */
		a {
			color: $accent;
			&:hover { color: #3D5CE5; }
		}

		/* ─── Scrollbar refinement ────────────────────── */
		::-webkit-scrollbar {
			width: 6px;
			height: 6px;
		}
		::-webkit-scrollbar-track {
			background: transparent;
		}
		::-webkit-scrollbar-thumb {
			background: #D1D5DB;
			border-radius: 3px;
			&:hover {
				background: #9CA3AF;
			}
		}
	</style>