/*
 * Overlays - Images, text or other things that can be rendered over the top of a ListView
 *
 * Author: Phillip Piper
 * Date: 14/04/2009 4:36 PM
 *
 * Change log:
 * 2009-08-10   JPP  - Added IDecoration interface
 * v2.2.1
 * 200-07-24    JPP  - TintedColumnDecoration now works when last item is a member of a collapsed
 *                     group (well, it no longer crashes).
 * v2.2
 * 2009-06-01   JPP  - Make sure that TintedColumnDecoration reaches to the last item in group view
 * 2009-05-05   JPP  - Unified BillboardOverlay text rendering with that of TextOverlay
 * 2009-04-30   JPP  - Added TintedColumnDecoration
 * 2009-04-14   JPP  - Initial version
 *
 * To do:
 *
 * Copyright (C) 2009 Phillip Piper
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * If you wish to use this code in a closed source application, please contact phillip_piper@bigfoot.com.
 */

using System;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;

namespace BrightIdeasSoftware
{
    /// <summary>
    /// The interface for an object which can draw itself over the top of
    /// an ObjectListView.
    /// </summary>
    public interface IOverlay
    {
        /// <summary>
        /// Draw this overlay
        /// </summary>
        /// <param name="olv">The ObjectListView that is being overlaid</param>
        /// <param name="g">The Graphics onto the given OLV</param>
        /// <param name="r">The content area of the OLV</param>
        void Draw(ObjectListView olv, Graphics g, Rectangle r);
    }

    /// <summary>
    /// A null implementation of the IOverlay interface
    /// </summary>
    public class AbstractOverlay : IOverlay
    {
        #region IOverlay Members

        /// <summary>
        /// Draw this overlay
        /// </summary>
        /// <param name="olv">The ObjectListView that is being overlaid</param>
        /// <param name="g">The Graphics onto the given OLV</param>
        /// <param name="r">The content area of the OLV</param>
        public virtual void Draw(ObjectListView olv, Graphics g, Rectangle r) {
        }

        #endregion
    }
    /*
    /// <summary>
    /// An overlay that can be positioned within the ObjectListView.
    /// </summary>
    [TypeConverter(typeof(BrightIdeasSoftware.Design.OverlayConverter))]
    public class GraphicOverlay : AbstractOverlay
    {
        #region Public properties

        /// <summary>
        /// Get or set where within the content rectangle of the listview this overlay should be drawn
        /// </summary>
        [Category("Appearance - ObjectListView"),
         Description("Where within the content rectangle of the listview the overlay will be drawn"),
         DefaultValue(System.Drawing.ContentAlignment.BottomRight),
         RefreshProperties(RefreshProperties.Repaint)]
        public System.Drawing.ContentAlignment Alignment {
            get { return this.overlayImageAlignment; }
            set { this.overlayImageAlignment = value; }
        }
        private System.Drawing.ContentAlignment overlayImageAlignment = System.Drawing.ContentAlignment.BottomRight;

        /// <summary>
        /// Gets or sets the number of pixels that this overlay will be inset of the horizontal edges of the
        /// ListViews content rectangle
        /// </summary>
        [Category("Appearance - ObjectListView"),
         Description("The number of pixels that the overlay will be inset from the horizontal edges of the ListViews content rectangle"),
         DefaultValue(20),
         NotifyParentProperty(true)]
        public int InsetX {
            get { return this.insetX; }
            set { this.insetX = Math.Max(0, value); }
        }
        private int insetX = 20;

        /// <summary>
        /// Gets or sets the number of pixels that this overlay will be inset from the vertical edges of the
        /// ListViews content rectangle
        /// </summary>
        [Category("Appearance - ObjectListView"),
         Description("The number of pixels that the overlay will be inset from the vertical edges of the ListViews content rectangle"),
         DefaultValue(20),
         NotifyParentProperty(true)]
        public int InsetY {
            get { return this.insetY; }
            set { this.insetY = Math.Max(0, value); }
        }
        private int insetY = 20;

        /// <summary>
        /// Gets or sets the degree of rotation by which the graphic will be transformed.
        /// The centre of rotation will be the center point of the graphic.
        /// </summary>
        [Category("Appearance - ObjectListView"),
         Description("The degree of rotation that will be applied to the graphic."),
         DefaultValue(0),
         NotifyParentProperty(true)]
        public int Rotation {
            get { return this.rotation; }
            set { this.rotation = value; }
        }
        private int rotation;

        #endregion

        #region Calculations

        /// <summary>
        /// Align a rectangle of the given size within the given bounds,
        /// obeying alignment and inset.
        /// </summary>
        /// <param name="bounds">The outer bounds</param>
        /// <param name="size">How big the rectangle should be</param>
        /// <returns>A rectangle</returns>
        protected Point CalculateAlignedLocation(Rectangle bounds, Size size) {
            Rectangle r = bounds;
            r.Inflate(-this.InsetX, -this.InsetY);

            Point pt = r.Location;
            switch (this.Alignment) {
                case System.Drawing.ContentAlignment.TopLeft:
                    return new Point(r.X, r.Top);
                case System.Drawing.ContentAlignment.TopCenter:
                    return new Point(r.X + ((r.Width - size.Width) / 2), r.Top);
                case System.Drawing.ContentAlignment.TopRight:
                    return new Point(r.Right - size.Width, r.Top);
                case System.Drawing.ContentAlignment.MiddleLeft:
                    return new Point(r.X, r.Y + ((r.Height - size.Height) / 2));
                case System.Drawing.ContentAlignment.MiddleCenter:
                    return new Point(r.X + ((r.Width - size.Width) / 2), r.Y + ((r.Height - size.Height) / 2));
                case System.Drawing.ContentAlignment.MiddleRight:
                    return new Point(r.Right - size.Width, r.Y + ((r.Height - size.Height) / 2));
                case System.Drawing.ContentAlignment.BottomLeft:
                    return new Point(r.X, r.Bottom - size.Height);
                case System.Drawing.ContentAlignment.BottomCenter:
                    return new Point(r.X + ((r.Width - size.Width) / 2), r.Bottom - size.Height);
                case System.Drawing.ContentAlignment.BottomRight:
                    return new Point(r.Right - size.Width, r.Bottom - size.Height);
            }

            // Should never reach here
            return bounds.Location;
        }

        /// <summary>
        /// Apply any specified rotation to the Graphic content.
        /// </summary>
        /// <param name="g">The Graphics to be transformed</param>
        /// <param name="r">The rotation will be around the centre of this rect</param>
        protected void ApplyRotation(Graphics g, Rectangle r) {
            if (this.Rotation == 0)
                return;

            // THINK: Do we want to reset the transform? I think we want to push a new transform
            g.ResetTransform();
            Matrix m = new Matrix();
            m.RotateAt(this.Rotation, new Point(r.Left + r.Width / 2, r.Top + r.Height / 2));
            g.Transform = m;
        }

        /// <summary>
        /// Reverse the rotation created by ApplyRotation()
        /// </summary>
        /// <param name="g"></param>
        protected void UnapplyRotation(Graphics g) {
            if (this.Rotation != 0)
                g.ResetTransform();
        }

        #endregion
    }
    */
    /// <summary>
    /// An overlay that will draw an image over the top of the ObjectListView
    /// </summary>
    [TypeConverter(typeof(BrightIdeasSoftware.Design.OverlayConverter))]
    public class ImageOverlay : ImageAdornment, IOverlay
    {
        public ImageOverlay() {
            this.Alignment = ContentAlignment.BottomRight;
        }

        #region Public properties

        /// <summary>
        /// Gets or sets the horizontal inset by which the position of the overlay will be adjusted
        /// </summary>
        [Category("Appearance - ObjectListView"),
         Description("The horizontal inset by which the position of the overlay will be adjusted"),
         DefaultValue(20),
         NotifyParentProperty(true)]
        public int InsetX {
            get { return this.insetX; }
            set { this.insetX = Math.Max(0, value); }
        }
        private int insetX = 20;

        /// <summary>
        /// Gets or sets the vertical inset by which the position of the overlay will be adjusted
        /// </summary>
        [Category("Appearance - ObjectListView"),
         Description("Gets or sets the vertical inset by which the position of the overlay will be adjusted"),
         DefaultValue(20),
         NotifyParentProperty(true)]
        public int InsetY {
            get { return this.insetY; }
            set { this.insetY = Math.Max(0, value); }
        }
        private int insetY = 20;

        #endregion

        #region Commands

        /// <summary>
        /// Draw this overlay
        /// </summary>
        /// <param name="olv">The ObjectListView being decorated</param>
        /// <param name="g">The Graphics used for drawing</param>
        /// <param name="r">The bounds of the rendering</param>
        public virtual void Draw(ObjectListView olv, Graphics g, Rectangle r) {
            Rectangle insetRect = r;
            insetRect.Inflate(-this.InsetX, -this.InsetY);
            this.DrawImage(g, insetRect);
        }

        #endregion
    }

    /// <summary>
    /// An overlay that will draw text over the top of the ObjectListView
    /// </summary>
    [TypeConverter(typeof(BrightIdeasSoftware.Design.OverlayConverter))]
    public class TextOverlay : TextAdornment, IOverlay
    {
        public TextOverlay() {
            // All text overlays draw at 100% opaque since the transparency is handled by 
            // glass panel onto which they are drawn
            this.Transparency = 255;
            this.Alignment = ContentAlignment.BottomRight;
        }

        #region Public properties

        /// <summary>
        /// Gets or sets the horizontal inset by which the position of the overlay will be adjusted
        /// </summary>
        [Category("Appearance - ObjectListView"),
         Description("The horizontal inset by which the position of the overlay will be adjusted"),
         DefaultValue(20),
         NotifyParentProperty(true)]
        public int InsetX {
            get { return this.insetX; }
            set { this.insetX = Math.Max(0, value); }
        }
        private int insetX = 20;

        /// <summary>
        /// Gets or sets the vertical inset by which the position of the overlay will be adjusted
        /// </summary>
        [Category("Appearance - ObjectListView"),
         Description("Gets or sets the vertical inset by which the position of the overlay will be adjusted"),
         DefaultValue(20),
         NotifyParentProperty(true)]
        public int InsetY {
            get { return this.insetY; }
            set { this.insetY = Math.Max(0, value); }
        }
        private int insetY = 20;

        /// <summary>
        /// Gets or sets whether the border will be drawn with rounded corners
        /// </summary>
        [Category("Appearance - ObjectListView"),
         Description("Will the border be drawn with rounded corners"),
         DefaultValue(true),
         Obsolete("Ise CornerRounding instead", false),
         DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
        public bool RoundCorneredBorder {
            get { return this.CornerRounding > 0; }
            set {
                if (value)
                    this.CornerRounding = 16.0f;
                else
                    this.CornerRounding = 0.0f;
            }
        }

        #endregion

        #region Commands

        /// <summary>
        /// Draw this overlay
        /// </summary>
        /// <param name="olv">The ObjectListView being decorated</param>
        /// <param name="g">The Graphics used for drawing</param>
        /// <param name="r">The bounds of the rendering</param>
        public virtual void Draw(ObjectListView olv, Graphics g, Rectangle r) {
            Rectangle insetRect = r;
            insetRect.Inflate(-this.InsetX, -this.InsetY);
            this.DrawText(g, insetRect);
        }

        #endregion
    }

    /// <summary>
    /// A Billboard overlay is positioned at an absolute point
    /// </summary>
    public class BillboardOverylay : TextOverlay
    {
        public BillboardOverylay() {
            this.BackColor = Color.PeachPuff;
            this.TextColor = Color.Black;
            this.BorderColor = Color.Empty;
            this.Font = new Font("Tahoma", 10);
        }

        /// <summary>
        /// Gets or sets where should the top left of the billboard be placed
        /// </summary>
        public Point Location {
            get { return this.location; }
            set { this.location = value; }
        }
        private Point location;

        /// <summary>
        /// Draw this overlay
        /// </summary>
        /// <param name="olv">The ObjectListView being decorated</param>
        /// <param name="g">The Graphics used for drawing</param>
        /// <param name="r">The bounds of the rendering</param>
        public override void Draw(ObjectListView olv, Graphics g, Rectangle r) {
            if (String.IsNullOrEmpty(this.Text))
                return;

            // Calculate the bounds of the text, and then move it to where it should be
            Rectangle textRect = this.CalculateTextBounds(g, r, this.Text);
            textRect.Location = this.Location;

            // Make sure the billboard is within the bounds of the List, as far as is possible
            if (textRect.Right > r.Width)
                textRect.X = Math.Max(r.Left, r.Width - textRect.Width);
            if (textRect.Bottom > r.Height)
                textRect.Y = Math.Max(r.Top, r.Height - textRect.Height);

            this.DrawBorderedText(g, textRect, this.Text);
        }
    }
}
